import { useState } from 'react';
import { Activity, Loader2, RefreshCw, TimerReset, XCircle } from 'lucide-react';
import { ConversionIcon, findConversionPair } from '../../../entities/conversion';
import { isActiveJobStatus, JobStatusBadge, useJobsHistory } from '../../../entities/job';
import { DeleteJobButton } from '../../../features/delete-job';
import { DownloadJobButton } from '../../../features/download-job-result';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { Alert, AlertDescription } from '../../../shared/ui/alert';
import { Button } from '../../../shared/ui/button';
import { Card, CardAction, CardContent, CardHeader, CardTitle } from '../../../shared/ui/card';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '../../../shared/ui/empty';
import { Item, ItemActions, ItemContent, ItemDescription, ItemMedia, ItemTitle } from '../../../shared/ui/item';
import { Progress } from '../../../shared/ui/progress';

function progressForStatus(status: string, progress?: number | null) {
  if (typeof progress === 'number') return progress;
  if (status === 'PROCESSING') return 60;
  if (status === 'QUEUED') return 15;
  return 5;
}

export function ActiveJobsWidget() {
  const jobs = useJobsHistory();
  const [actionError, setActionError] = useState<string | null>(null);
  const activeJobs = (jobs.data ?? []).filter((job) => isActiveJobStatus(job.status));

  return (
    <section aria-label="Trabajos en proceso">
      <Card className="min-h-[540px]">
        <CardHeader className="border-b-2 border-border pb-6">
          <div className="grid gap-2">
            <span className="font-mono text-[0.65rem] font-black tracking-[0.16em] text-primary uppercase">Live queue / {activeJobs.length} activos</span>
            <CardTitle className="text-3xl font-black tracking-[-0.06em] sm:text-4xl">En proceso ahora.</CardTitle>
            <p className="max-w-xl text-base font-medium text-muted-foreground">La cola se actualiza automáticamente. Puedes seguir trabajando mientras cada archivo termina.</p>
          </div>
          <CardAction>
            <Button variant="outline" type="button" onClick={() => void jobs.refetch()} disabled={jobs.isFetching} aria-label="Actualizar trabajos activos">
              {jobs.isFetching ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="size-4" aria-hidden="true" />}
              <span className="hidden sm:inline">Actualizar</span>
            </Button>
          </CardAction>
        </CardHeader>

        <CardContent className="grid gap-4 pt-6">
          {activeJobs.length === 0 && !jobs.isLoading && (
            <Empty className="min-h-64 border-2 border-dashed border-border bg-background">
              <EmptyHeader>
                <EmptyMedia variant="icon" className="border-2 border-border bg-accent">
                  <TimerReset className="size-4" aria-hidden="true" />
                </EmptyMedia>
                <EmptyTitle className="text-xl font-black tracking-[-0.04em]">La cola está despejada.</EmptyTitle>
                <EmptyDescription>Cuando inicies una conversión, verás aquí su progreso en tiempo real.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          )}

          {activeJobs.map((job) => {
            const pair = findConversionPair(job.source_format, job.target_format);
            const value = progressForStatus(job.status, job.progress_percent);

            return (
              <Item key={job.job_id} variant="muted" className="gap-4 p-4">
                <ItemMedia variant="icon" className="size-11 border-2 border-border bg-primary text-primary-foreground">
                  <ConversionIcon category={pair?.category} className="size-5" />
                </ItemMedia>
                <ItemContent className="min-w-0 gap-2">
                  <ItemTitle className="max-w-full justify-between gap-3 text-base font-black">
                    <span className="truncate">{job.source_format.toUpperCase()} → {job.target_format.toUpperCase()}</span>
                    <JobStatusBadge status={job.status} withIcon />
                  </ItemTitle>
                  <ItemDescription className="flex flex-wrap gap-x-3 gap-y-1 font-mono text-[0.68rem] uppercase">
                    <span>{formatBytes(job.file_size)}</span>
                    <span>{job.progress_stage ?? 'Procesando'}</span>
                    <span>{value}%</span>
                  </ItemDescription>
                  <Progress value={value} className="h-2" />
                </ItemContent>
                <ItemActions>
                  <DownloadJobButton job={job} variant="icon" onError={setActionError} />
                  <DeleteJobButton jobId={job.job_id} onError={setActionError} />
                </ItemActions>
              </Item>
            );
          })}

          {jobs.error && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>{jobs.error instanceof Error ? jobs.error.message : 'No se pudo consultar la cola.'}</AlertDescription>
            </Alert>
          )}
          {actionError && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>{actionError}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
