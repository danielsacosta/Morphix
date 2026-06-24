import { ArrowDownToLine, Loader2 } from 'lucide-react';
import { useDownloadJobResult } from '../model/useDownloadJobResult';
import type { JobRecord } from '../../../entities/job';
import { Button } from '../../../shared/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../../shared/ui/tooltip';

interface DownloadJobButtonProps {
  job: JobRecord;
  variant?: 'icon' | 'text';
  onError?: (message: string) => void;
}

export function DownloadJobButton({ job, variant = 'text', onError }: DownloadJobButtonProps) {
  const download = useDownloadJobResult(onError);
  const disabled = job.status !== 'COMPLETED' || download.isPending;

  if (variant === 'icon') {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline" size="icon" type="button" onClick={() => download.mutate(job)} disabled={disabled} aria-label="Descargar resultado">
            {download.isPending ? (
              <Loader2 className="size-4 animate-spin" aria-hidden="true" />
            ) : (
              <ArrowDownToLine className="size-4" aria-hidden="true" />
            )}
          </Button>
        </TooltipTrigger>
        <TooltipContent>Descargar resultado</TooltipContent>
      </Tooltip>
    );
  }

  return (
    <Button variant="outline" type="button" onClick={() => download.mutate(job)} disabled={disabled}>
      {download.isPending ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <ArrowDownToLine className="size-4" aria-hidden="true" />}
      Descargar
    </Button>
  );
}
