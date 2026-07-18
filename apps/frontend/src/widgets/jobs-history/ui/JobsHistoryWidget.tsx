import { useState } from 'react';
import { Clock3, Loader2, RefreshCw, XCircle } from 'lucide-react';
import { ConversionIcon, findConversionPair } from '../../../entities/conversion';
import { JobHistoryRow, useJobsHistory } from '../../../entities/job';
import { DeleteJobButton } from '../../../features/delete-job';
import { DownloadJobButton } from '../../../features/download-job-result';
import { Alert, AlertDescription } from '../../../shared/ui/alert';
import { Button } from '../../../shared/ui/button';
import { Card, CardAction, CardContent, CardHeader, CardTitle } from '../../../shared/ui/card';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '../../../shared/ui/empty';

export function JobsHistoryWidget() {
  const jobs = useJobsHistory();
  const [actionError, setActionError] = useState<string | null>(null);

  return (
    <section id="history" aria-label="Historial de conversiones" className="scroll-mt-24">
      <Card>
        <CardHeader className="border-b-2 border-border pb-6">
          <div className="space-y-1">
            <span className="font-mono text-[0.65rem] font-black tracking-[0.16em] text-primary uppercase">Archive / session history</span>
            <CardTitle className="text-3xl font-black tracking-[-0.06em] sm:text-4xl">Conversiones recientes.</CardTitle>
            <p className="text-base font-medium text-muted-foreground">Resultados disponibles para descargar o eliminar.</p>
          </div>
          <CardAction>
            <Button variant="outline" type="button" onClick={() => void jobs.refetch()} disabled={jobs.isFetching}>
              {jobs.isFetching ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="size-4" aria-hidden="true" />}
              <span>Actualizar</span>
            </Button>
          </CardAction>
        </CardHeader>

        <CardContent className="grid content-start gap-3 pt-6">
          {jobs.data?.length === 0 && (
            <Empty className="min-h-64 border-2 border-dashed border-border bg-background">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Clock3 className="size-4" aria-hidden="true" />
                </EmptyMedia>
                <EmptyTitle className="text-xl font-black tracking-[-0.04em]">Sin conversiones registradas</EmptyTitle>
                <EmptyDescription>Todavía no hay archivos procesados en esta sesión.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          )}

          {jobs.data?.map((job) => {
            const pair = findConversionPair(job.source_format, job.target_format);

            return (
              <JobHistoryRow
                key={job.job_id}
                job={job}
                leadingIcon={<ConversionIcon category={pair?.category} className="size-5" />}
                actions={
                  <>
                    <DownloadJobButton job={job} variant="icon" onError={setActionError} />
                    <DeleteJobButton jobId={job.job_id} onError={setActionError} />
                  </>
                }
              />
            );
          })}

          {jobs.error && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>{jobs.error instanceof Error ? jobs.error.message : 'No se pudo consultar el historial.'}</AlertDescription>
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
