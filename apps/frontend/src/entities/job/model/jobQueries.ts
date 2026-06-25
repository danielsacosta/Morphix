export const jobQueries = {
  all: ['jobs'] as const,
  list: () => [...jobQueries.all, 'list'] as const,
  batch: (batchId: string) => [...jobQueries.all, 'batch', batchId] as const,
  detail: (jobId: string) => [...jobQueries.all, 'detail', jobId] as const,
};
