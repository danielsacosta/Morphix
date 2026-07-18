import { CheckCircle2, XCircle } from 'lucide-react';
import { cn } from '../../../shared/lib/utils';
import { Badge } from '../../../shared/ui/badge';
import { statusLabel } from '../model/jobStatus';
import type { JobStatus } from '../model/jobTypes';

interface JobStatusBadgeProps {
  status: JobStatus;
  withIcon?: boolean;
}

const statusClassName: Record<JobStatus, string> = {
  PENDING: 'border-border bg-muted text-muted-foreground',
  UPLOAD_REQUESTED: 'border-border bg-accent text-accent-foreground',
  UPLOADED: 'border-border bg-accent text-accent-foreground',
  QUEUED: 'border-border bg-secondary text-foreground',
  PROCESSING: 'border-border bg-accent text-accent-foreground',
  COMPLETED: 'border-border bg-primary text-primary-foreground',
  FAILED: 'border-border bg-destructive text-white',
  EXPIRED: 'border-border bg-destructive text-white',
  DELETED: 'border-border bg-muted text-muted-foreground',
};

export function JobStatusBadge({ status, withIcon = false }: JobStatusBadgeProps) {
  return (
    <Badge variant="outline" className={cn('gap-1.5', statusClassName[status])}>
      {withIcon && status === 'COMPLETED' && <CheckCircle2 className="size-3" aria-hidden="true" />}
      {withIcon && status === 'FAILED' && <XCircle className="size-3" aria-hidden="true" />}
      {statusLabel[status]}
    </Badge>
  );
}
