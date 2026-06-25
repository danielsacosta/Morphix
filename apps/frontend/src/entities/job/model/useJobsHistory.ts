import { useQuery } from '@tanstack/react-query';
import { listJobs } from '../api/jobsApi';
import { jobQueries } from './jobQueries';

export function useJobsHistory() {
  return useQuery({
    queryKey: jobQueries.list(),
    queryFn: () => listJobs(),
    staleTime: 10_000,
  });
}
