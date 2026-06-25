import { useEffect, useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { normalizeExtension } from '../../../entities/conversion';
import { isActiveJobStatus, jobQueries, useBatchJobsPolling, type JobRecord } from '../../../entities/job';
import { env } from '../../../shared/config/env';
import { createBatchJobs, getUploadUrl, startJob, uploadFile } from '../api/convertFileApi';
import { busyFlowStates, type FlowState } from './convertFileTypes';

const MAX_BATCH_FILES = 10;

export interface QueuedConversionFile {
  id: string;
  file: File;
  sourceFormat: string;
  job?: JobRecord;
  error?: string;
}

function buildQueueItem(file: File): QueuedConversionFile {
  const id = typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${file.name}-${file.size}-${Date.now()}`;

  return {
    id,
    file,
    sourceFormat: normalizeExtension(file.name),
  };
}

function upsertJobs(previous: JobRecord[] | undefined, jobs: JobRecord[]): JobRecord[] {
  const existing = previous ?? [];
  const nextJobs = jobs.map((job) => job.job_id);
  return [...jobs, ...existing.filter((item) => !nextJobs.includes(item.job_id))];
}

function mergePolledJobs(queue: QueuedConversionFile[], jobs: JobRecord[]): QueuedConversionFile[] {
  const byId = new Map(jobs.map((job) => [job.job_id, job]));
  return queue.map((item) => {
    if (!item.job) return item;
    return { ...item, job: byId.get(item.job.job_id) ?? item.job };
  });
}

function sortJobsByQueuePosition(jobs: JobRecord[]): JobRecord[] {
  return [...jobs].sort((a, b) => (a.queue_position ?? 0) - (b.queue_position ?? 0));
}

export function useConvertFile() {
  const queryClient = useQueryClient();
  const [queue, setQueue] = useState<QueuedConversionFile[]>([]);
  const [batchId, setBatchId] = useState<string | null>(null);
  const [flowState, setFlowState] = useState<FlowState>('idle');
  const [error, setError] = useState<string | null>(null);

  const currentJobs = useMemo(() => queue.map((item) => item.job).filter(Boolean) as JobRecord[], [queue]);
  const polledBatch = useBatchJobsPolling(batchId, currentJobs);
  const sourceFormat = useMemo(() => {
    const formats = new Set(queue.map((item) => item.sourceFormat).filter(Boolean));
    return formats.size === 1 ? [...formats][0] : '';
  }, [queue]);
  const mixedSourceFormats = queue.length > 1 && !sourceFormat;
  const oversizedFiles = queue.filter((item) => item.file.size > env.maxFileSizeBytes);
  const fileTooLarge = oversizedFiles.length > 0;
  const activeCount = currentJobs.filter((job) => isActiveJobStatus(job.status)).length;
  const completedCount = currentJobs.filter((job) => job.status === 'COMPLETED').length;
  const failedCount = currentJobs.filter((job) => job.status === 'FAILED').length + queue.filter((item) => item.error).length;
  const canStart = useMemo(
    () => Boolean(queue.length > 0 && !fileTooLarge && !mixedSourceFormats && !busyFlowStates.includes(flowState)),
    [fileTooLarge, flowState, mixedSourceFormats, queue.length],
  );

  useEffect(() => {
    if (!polledBatch.data || polledBatch.data.length === 0) return;

    const jobs = sortJobsByQueuePosition(polledBatch.data);
    setQueue((previous) => mergePolledJobs(previous, jobs));
    queryClient.setQueryData<JobRecord[]>(jobQueries.list(), (previous) => upsertJobs(previous, jobs));

    if (jobs.some((job) => isActiveJobStatus(job.status))) return;

    setFlowState(jobs.every((job) => job.status === 'FAILED') ? 'failed' : 'ready');
    if (jobs.some((job) => job.status === 'FAILED')) {
      setError('Uno o más archivos no se pudieron convertir. Revisa el detalle de cada fila.');
    }
    void queryClient.invalidateQueries({ queryKey: jobQueries.list() });
  }, [polledBatch.data, queryClient]);

  useEffect(() => {
    if (polledBatch.error) {
      setFlowState('failed');
      setError(polledBatch.error instanceof Error ? polledBatch.error.message : 'No se pudo consultar el estado del lote.');
    }
  }, [polledBatch.error]);

  function selectFiles(fileList: FileList | File[] | null) {
    const files = Array.from(fileList ?? []);
    const acceptedFiles = files.slice(0, MAX_BATCH_FILES);
    setQueue(acceptedFiles.map(buildQueueItem));
    setBatchId(null);
    setFlowState('idle');
    setError(files.length > MAX_BATCH_FILES ? `Solo se agregaron los primeros ${MAX_BATCH_FILES} archivos.` : null);
  }

  function clearQueue() {
    setQueue([]);
    setBatchId(null);
    setFlowState('idle');
    setError(null);
  }

  async function convert(targetFormat: string) {
    if (!targetFormat || !canStart) return;

    setError(null);
    setFlowState('creating');

    try {
      const files = queue.map((item) => item.file);
      const created = await createBatchJobs(files, targetFormat);
      const createdJobs = sortJobsByQueuePosition(created.jobs);
      setBatchId(created.batch_id);
      setQueue((previous) => previous.map((item, index) => ({ ...item, job: createdJobs[index] })));
      queryClient.setQueryData<JobRecord[]>(jobQueries.list(), (previous) => upsertJobs(previous, createdJobs));

      setFlowState('uploading');
      for (const [index, item] of queue.entries()) {
        const job = createdJobs[index];
        const upload = await getUploadUrl(job.job_id, item.file.type);
        await uploadFile(upload, item.file);
      }

      setFlowState('starting');
      const startedJobs: JobRecord[] = [];
      for (const job of createdJobs) {
        startedJobs.push(await startJob(job.job_id));
      }

      const startedById = new Map(startedJobs.map((job) => [job.job_id, job]));
      setQueue((previous) =>
        previous.map((item) => ({
          ...item,
          job: item.job ? startedById.get(item.job.job_id) ?? item.job : item.job,
        })),
      );
      queryClient.setQueryData<JobRecord[]>(jobQueries.list(), (previous) => upsertJobs(previous, startedJobs));
      setFlowState(startedJobs.some((job) => isActiveJobStatus(job.status)) ? 'polling' : 'ready');
      void queryClient.invalidateQueries({ queryKey: jobQueries.list() });
    } catch (conversionError) {
      setFlowState('failed');
      setError(conversionError instanceof Error ? conversionError.message : 'La conversión no pudo iniciarse.');
    }
  }

  return {
    batchId,
    queue,
    files: queue.map((item) => item.file),
    sourceFormat,
    mixedSourceFormats,
    fileTooLarge,
    oversizedFiles,
    currentJobs,
    activeCount,
    completedCount,
    failedCount,
    flowState,
    error,
    canStart,
    maxBatchFiles: MAX_BATCH_FILES,
    maxFileSizeMb: env.maxFileSizeMb,
    selectFiles,
    clearQueue,
    convert,
    setError,
  };
}
