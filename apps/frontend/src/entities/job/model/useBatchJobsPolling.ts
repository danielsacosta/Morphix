import { useQuery } from '@tanstack/react-query';
import { listJobs } from '../api/jobsApi';
import { isActiveJobStatus } from './jobStatus';
import { jobQueries } from './jobQueries';
import type { JobRecord } from './jobTypes';

export function useBatchJobsPolling(batchId?: string | null, initialJobs: JobRecord[] = []) {
  return useQuery({
    queryKey: batchId ? jobQueries.batch(batchId) : jobQueries.batch('idle'),
    queryFn: () => listJobs(batchId!),
    enabled: Boolean(batchId),
    initialData: initialJobs.length > 0 ? initialJobs : undefined,
    refetchInterval: (query) => {
      const jobs = query.state.data ?? [];
      return jobs.some((job) => isActiveJobStatus(job.status)) ? 2000 : false;
    },
    refetchIntervalInBackground: true,
    retry: 1,
  });
}
