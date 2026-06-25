import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { env } from '../../../shared/config/env';
import { getStoredUserId } from '../../../shared/lib/userSession';
import { jobQueries } from './jobQueries';
import type { JobRecord } from './jobTypes';

interface JobUpdatedEvent {
  type: 'job.updated';
  job: JobRecord;
}

function sortByCreatedAt(jobs: JobRecord[]): JobRecord[] {
  return [...jobs].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
}

function sortByQueuePosition(jobs: JobRecord[]): JobRecord[] {
  return [...jobs].sort((a, b) => (a.queue_position ?? 0) - (b.queue_position ?? 0));
}

function upsertJob(previous: JobRecord[] | undefined, job: JobRecord, sorter: (jobs: JobRecord[]) => JobRecord[]): JobRecord[] {
  const jobs = previous ?? [];
  const next = jobs.some((item) => item.job_id === job.job_id) ? jobs.map((item) => (item.job_id === job.job_id ? { ...item, ...job } : item)) : [job, ...jobs];
  return sorter(next);
}

function buildSocketUrl(baseUrl: string, userId: string): string {
  const url = new URL(baseUrl);
  url.searchParams.set('user_id', userId);
  return url.toString();
}

export function useJobRealtime() {
  const queryClient = useQueryClient();

  useEffect(() => {
    const websocketApiUrl = env.websocketApiUrl;
    if (!websocketApiUrl || typeof window === 'undefined') return;

    let closed = false;
    let attempts = 0;
    let socket: WebSocket | null = null;
    let reconnectTimer: number | undefined;

    const connect = () => {
      socket = new WebSocket(buildSocketUrl(websocketApiUrl, getStoredUserId()));

      socket.onopen = () => {
        attempts = 0;
      };

      socket.onmessage = (message) => {
        let event: JobUpdatedEvent;
        try {
          event = JSON.parse(message.data) as JobUpdatedEvent;
        } catch {
          return;
        }
        if (event.type !== 'job.updated' || !event.job?.job_id) return;

        queryClient.setQueryData<JobRecord>(jobQueries.detail(event.job.job_id), (previous) => (previous ? { ...previous, ...event.job } : event.job));
        queryClient.setQueryData<JobRecord[]>(jobQueries.list(), (previous) => upsertJob(previous, event.job, sortByCreatedAt));

        if (event.job.batch_id) {
          queryClient.setQueryData<JobRecord[]>(jobQueries.batch(event.job.batch_id), (previous) => upsertJob(previous, event.job, sortByQueuePosition));
        }
      };

      socket.onclose = () => {
        if (closed) return;
        attempts += 1;
        reconnectTimer = window.setTimeout(connect, Math.min(10_000, attempts * 1_500));
      };
    };

    connect();

    return () => {
      closed = true;
      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer);
      }
      socket?.close();
    };
  }, [queryClient]);
}
