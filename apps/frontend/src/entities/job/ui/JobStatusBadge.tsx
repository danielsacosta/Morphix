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
  PENDING: 'border-muted-foreground/25 bg-muted/40 text-muted-foreground',
  UPLOAD_REQUESTED: 'border-primary/35 bg-primary/10 text-primary',
  UPLOADED: 'border-primary/35 bg-primary/10 text-primary',
  QUEUED: 'border-accent/35 bg-accent/10 text-accent',
  PROCESSING: 'border-accent/40 bg-accent/10 text-accent',
  COMPLETED: 'border-primary/45 bg-primary/15 text-primary',
  FAILED: 'border-destructive/45 bg-destructive/15 text-destructive',
  EXPIRED: 'border-destructive/45 bg-destructive/15 text-destructive',
  DELETED: 'border-muted-foreground/25 bg-muted/40 text-muted-foreground',
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
