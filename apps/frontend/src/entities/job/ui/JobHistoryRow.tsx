import type { ReactNode } from 'react';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { Item, ItemActions, ItemContent, ItemDescription, ItemMedia, ItemTitle } from '../../../shared/ui/item';
import type { JobRecord } from '../model/jobTypes';
import { JobStatusBadge } from './JobStatusBadge';

interface JobHistoryRowProps {
  job: JobRecord;
  leadingIcon: ReactNode;
  actions: ReactNode;
}

export function JobHistoryRow({ job, leadingIcon, actions }: JobHistoryRowProps) {
  return (
    <Item variant="muted" className="gap-3 border-border/60 bg-background/35">
      <ItemMedia variant="icon" className="size-11 rounded-lg bg-primary/10 text-primary ring-1 ring-primary/20">
        {leadingIcon}
      </ItemMedia>
      <ItemContent className="min-w-0">
        <ItemTitle className="max-w-full truncate">
          {job.source_format.toUpperCase()} a {job.target_format.toUpperCase()}
        </ItemTitle>
        <ItemDescription className="max-w-full truncate">
          {new Date(job.created_at).toLocaleString()} · {formatBytes(job.file_size)}
        </ItemDescription>
      </ItemContent>
      <JobStatusBadge status={job.status} withIcon />
      <ItemActions>{actions}</ItemActions>
    </Item>
  );
}
