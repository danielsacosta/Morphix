import { httpRequest } from '../../../shared/api/httpClient';
import type { DownloadUrlResponse, JobRecord } from '../model/jobTypes';

export async function getJob(jobId: string): Promise<JobRecord> {
  const response = await httpRequest<{ job: JobRecord }>(`/jobs/${jobId}`);
  return response.job;
}

export async function listJobs(batchId?: string): Promise<JobRecord[]> {
  const query = batchId ? `?batch_id=${encodeURIComponent(batchId)}` : '';
  const response = await httpRequest<{ jobs: JobRecord[] }>(`/jobs${query}`);
  return response.jobs.filter((job) => job.status !== 'DELETED');
}

export async function getDownloadUrl(jobId: string): Promise<DownloadUrlResponse> {
  return httpRequest<DownloadUrlResponse>(`/jobs/${jobId}/download-url`);
}

export async function deleteJob(jobId: string): Promise<void> {
  await httpRequest<{ job: JobRecord }>(`/jobs/${jobId}`, { method: 'DELETE' });
}
