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
    <section aria-label="Conversion history">
      <Card className="border-border/70 bg-card/85 shadow-2xl shadow-black/20 backdrop-blur">
        <CardHeader>
          <div className="space-y-1">
            <span className="text-xs font-semibold tracking-normal text-muted-foreground uppercase">Historial</span>
            <CardTitle className="text-2xl font-semibold tracking-normal sm:text-3xl">Conversiones recientes</CardTitle>
          </div>
          <CardAction>
            <Button variant="outline" type="button" onClick={() => void jobs.refetch()} disabled={jobs.isFetching}>
              {jobs.isFetching ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="size-4" aria-hidden="true" />}
              <span>Actualizar</span>
            </Button>
          </CardAction>
        </CardHeader>

        <CardContent className="grid gap-3">
          {jobs.data?.length === 0 && (
            <Empty className="min-h-32 border border-dashed border-border/70 bg-background/25">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <Clock3 className="size-4" aria-hidden="true" />
                </EmptyMedia>
                <EmptyTitle>Sin conversiones registradas</EmptyTitle>
                <EmptyDescription>No hay jobs para este usuario.</EmptyDescription>
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
