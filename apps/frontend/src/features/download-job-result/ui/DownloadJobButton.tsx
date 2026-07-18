import { useState } from 'react';
import { ArrowDownToLine, FileText, Loader2, XCircle } from 'lucide-react';
import { useDownloadJobResult } from '../model/useDownloadJobResult';
import { JobStatusBadge, statusLabel, type JobRecord } from '../../../entities/job';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { Alert, AlertDescription } from '../../../shared/ui/alert';
import { Button } from '../../../shared/ui/button';
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../shared/ui/dialog';
import { Separator } from '../../../shared/ui/separator';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../../shared/ui/tooltip';

interface DownloadJobButtonProps {
  job: JobRecord;
  variant?: 'icon' | 'text';
  onError?: (message: string) => void;
}

export function DownloadJobButton({ job, variant = 'text', onError }: DownloadJobButtonProps) {
  const [open, setOpen] = useState(false);
  const download = useDownloadJobResult(onError);
  const canDownload = job.status === 'COMPLETED';
  const routeLabel = `${job.source_format.toUpperCase()} a ${job.target_format.toUpperCase()}`;
  const inputName = fileNameFromKey(job.input_key);
  const outputName = job.output_key ? fileNameFromKey(job.output_key) : 'Resultado no disponible';
  const details = [
    { label: 'Archivo original', value: inputName },
    { label: 'Resultado', value: outputName },
    { label: 'Tamaño', value: formatBytes(job.file_size) },
    { label: 'Duración', value: formatDuration(job.duration_seconds) },
    { label: 'Creada', value: formatDate(job.created_at) },
    { label: 'Actualizada', value: formatDate(job.updated_at) },
  ];

  const trigger =
    variant === 'icon' ? (
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline" size="icon" type="button" onClick={() => setOpen(true)} aria-label="Ver detalles de descarga">
            <ArrowDownToLine className="size-4" aria-hidden="true" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Ver detalles de descarga</TooltipContent>
      </Tooltip>
    ) : (
      <Button variant="outline" type="button" onClick={() => setOpen(true)}>
        <ArrowDownToLine className="size-4" aria-hidden="true" />
        Descargar
      </Button>
    );

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {trigger}
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader className="pr-8">
          <div className="mb-2 flex size-11 items-center justify-center border-2 border-border bg-primary text-primary-foreground">
            <FileText className="size-5" aria-hidden="true" />
          </div>
          <DialogTitle>Detalles de descarga</DialogTitle>
          <DialogDescription>{routeLabel}</DialogDescription>
        </DialogHeader>

        <div className="grid gap-4">
          <div className="border-2 border-border bg-background p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="min-w-0">
                <p className="truncate text-base font-semibold text-foreground">{routeLabel}</p>
                <p className="mt-1 truncate text-sm text-muted-foreground">{inputName}</p>
              </div>
              <JobStatusBadge status={job.status} withIcon />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {details.map((detail) => (
              <div key={detail.label} className="border-2 border-border bg-secondary p-3">
                <p className="font-mono text-[0.62rem] font-black tracking-[0.1em] text-muted-foreground uppercase">{detail.label}</p>
                <p className="mt-1 break-words text-sm font-bold text-foreground">{detail.value}</p>
              </div>
            ))}
          </div>

          {job.error_message && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>{job.error_message}</AlertDescription>
            </Alert>
          )}

          {!canDownload && (
            <p className="text-sm text-muted-foreground">
              La descarga no está disponible porque la conversión está en estado {statusLabel[job.status].toLowerCase()}.
            </p>
          )}
        </div>

        <Separator />

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" type="button">
              Cerrar
            </Button>
          </DialogClose>
          <Button type="button" onClick={() => download.mutate(job)} disabled={!canDownload || download.isPending}>
            {download.isPending ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <ArrowDownToLine className="size-4" aria-hidden="true" />}
            Descargar resultado
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function fileNameFromKey(key: string): string {
  return decodeURIComponent(key.split('/').pop() || key);
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function formatDuration(value?: number | null): string {
  if (typeof value !== 'number') return 'No disponible';
  return `${value.toFixed(value >= 10 ? 1 : 2)} s`;
}
