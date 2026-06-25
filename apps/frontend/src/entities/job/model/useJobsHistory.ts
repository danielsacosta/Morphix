import { useQuery } from '@tanstack/react-query';
import { listJobs } from '../api/jobsApi';
import { jobQueries } from './jobQueries';
import type { JobRecord } from './jobTypes';

function visibleJobs(jobs: JobRecord[]): JobRecord[] {
  return jobs.filter((job) => job.status !== 'DELETED');
}

export function useJobsHistory() {
  return useQuery({
    queryKey: jobQueries.list(),
    queryFn: () => listJobs(),
    select: visibleJobs,
    staleTime: 10_000,
  });
}
