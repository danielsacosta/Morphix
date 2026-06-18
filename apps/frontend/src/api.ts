import { config, getUserId } from './config';
import type { CreateJobResponse, DownloadUrlResponse, JobRecord, UploadUrlResponse } from './types';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${config.apiBaseUrl}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': getUserId(),
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail || payload.message || message;
    } catch {
      // Ignore invalid JSON error bodies.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function createJob(file: File, targetFormat: string): Promise<CreateJobResponse> {
  const sourceFormat = file.name.split('.').pop()?.toLowerCase() === 'jpeg'
    ? 'jpg'
    : file.name.split('.').pop()?.toLowerCase();

  return request<CreateJobResponse>('/jobs', {
    method: 'POST',
    body: JSON.stringify({
      filename: file.name,
      file_size: file.size,
      content_type: file.type || 'application/octet-stream',
      source_format: sourceFormat,
      target_format: targetFormat,
    }),
  });
}

export async function getUploadUrl(jobId: string, contentType: string): Promise<UploadUrlResponse> {
  return request<UploadUrlResponse>(`/jobs/${jobId}/upload-url`, {
    method: 'POST',
    body: JSON.stringify({ content_type: contentType || 'application/octet-stream' }),
  });
}

export async function uploadFile(upload: UploadUrlResponse, file: File): Promise<void> {
  const response = await fetch(upload.upload_url, {
    method: upload.method,
    headers: upload.headers,
    body: file,
  });

  if (!response.ok) {
    throw new Error(`Upload failed with status ${response.status}`);
  }
}

export async function startJob(jobId: string): Promise<JobRecord> {
  const response = await request<{ job: JobRecord }>(`/jobs/${jobId}/start`, { method: 'POST' });
  return response.job;
}

export async function getJob(jobId: string): Promise<JobRecord> {
  const response = await request<{ job: JobRecord }>(`/jobs/${jobId}`);
  return response.job;
}

export async function listJobs(): Promise<JobRecord[]> {
  const response = await request<{ jobs: JobRecord[] }>('/jobs');
  return response.jobs;
}

export async function getDownloadUrl(jobId: string): Promise<DownloadUrlResponse> {
  return request<DownloadUrlResponse>(`/jobs/${jobId}/download-url`);
}

export async function deleteJob(jobId: string): Promise<void> {
  await request<{ job: JobRecord }>(`/jobs/${jobId}`, { method: 'DELETE' });
}

