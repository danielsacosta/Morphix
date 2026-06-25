import { normalizeExtension } from '../../../entities/conversion';
import type { CreateBatchJobsResponse, CreateJobResponse, JobRecord, UploadUrlResponse } from '../../../entities/job';
import { httpRequest } from '../../../shared/api/httpClient';

export async function createJob(file: File, targetFormat: string): Promise<CreateJobResponse> {
  return httpRequest<CreateJobResponse>('/jobs', {
    method: 'POST',
    body: JSON.stringify({
      filename: file.name,
      file_size: file.size,
      content_type: file.type || 'application/octet-stream',
      source_format: normalizeExtension(file.name),
      target_format: targetFormat,
    }),
  });
}

export async function createBatchJobs(files: File[], targetFormat: string): Promise<CreateBatchJobsResponse> {
  return httpRequest<CreateBatchJobsResponse>('/jobs/batch', {
    method: 'POST',
    body: JSON.stringify({
      files: files.map((file) => ({
        filename: file.name,
        file_size: file.size,
        content_type: file.type || 'application/octet-stream',
        source_format: normalizeExtension(file.name),
        target_format: targetFormat,
      })),
    }),
  });
}

export async function getUploadUrl(jobId: string, contentType: string): Promise<UploadUrlResponse> {
  return httpRequest<UploadUrlResponse>(`/jobs/${jobId}/upload-url`, {
    method: 'POST',
    body: JSON.stringify({ content_type: contentType || 'application/octet-stream' }),
  });
}

export async function uploadFile(upload: UploadUrlResponse, file: File): Promise<void> {
  let response: Response;

  try {
    response = await fetch(upload.upload_url, {
      method: upload.method,
      headers: upload.headers,
      body: file,
    });
  } catch {
    throw new Error('No se pudo cargar el archivo. Inténtalo de nuevo en unos minutos.');
  }

  if (!response.ok) {
    throw new Error(`La carga del archivo no se pudo completar. Código ${response.status}.`);
  }
}

export async function startJob(jobId: string): Promise<JobRecord> {
  const response = await httpRequest<{ job: JobRecord }>(`/jobs/${jobId}/start`, { method: 'POST' });
  return response.job;
}
