export type JobStatus =
  | 'PENDING'
  | 'UPLOAD_REQUESTED'
  | 'UPLOADED'
  | 'QUEUED'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED'
  | 'EXPIRED'
  | 'DELETED';

export interface JobRecord {
  job_id: string;
  user_id: string;
  input_key: string;
  output_key?: string | null;
  source_format: string;
  target_format: string;
  status: JobStatus;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
  expires_at: number;
  file_size: number;
  duration_seconds?: number | null;
  state_machine_execution_arn?: string | null;
  batch_id?: string | null;
  queue_position?: number | null;
  queued_at?: string | null;
  queue_message_id?: string | null;
}

export interface CreateJobResponse {
  job: JobRecord;
}

export interface CreateBatchJobsResponse {
  batch_id: string;
  jobs: JobRecord[];
}

export interface UploadUrlResponse {
  upload_url: string;
  method: 'PUT';
  expires_in: number;
  headers: Record<string, string>;
}

export interface DownloadUrlResponse {
  download_url: string;
  expires_in: number;
}
