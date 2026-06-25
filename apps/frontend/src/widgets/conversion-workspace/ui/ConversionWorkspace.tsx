import { useMemo, useRef } from 'react';
import { FileText, Layers3, Trash2, UploadCloud, XCircle } from 'lucide-react';
import { acceptedExtensions, ConversionRouteSummary } from '../../../entities/conversion';
import { JobStatusBadge } from '../../../entities/job';
import { ConvertButton, ConversionProgress, useConvertFile } from '../../../features/convert-file';
import { DownloadJobButton } from '../../../features/download-job-result';
import { TargetFormatGrid, useTargetFormat } from '../../../features/select-target-format';
import { env } from '../../../shared/config/env';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { cn } from '../../../shared/lib/utils';
import { Alert, AlertDescription } from '../../../shared/ui/alert';
import { Button } from '../../../shared/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../../shared/ui/card';
import { Input } from '../../../shared/ui/input';
import { Item, ItemActions, ItemContent, ItemDescription, ItemGroup, ItemMedia, ItemTitle } from '../../../shared/ui/item';
import { Label } from '../../../shared/ui/label';
import { Progress } from '../../../shared/ui/progress';

export function ConversionWorkspace() {
  const inputRef = useRef<HTMLInputElement>(null);
  const conversion = useConvertFile();
  const target = useTargetFormat(conversion.sourceFormat);
  const acceptedFormatsLabel = acceptedExtensions().replaceAll('.', '').toUpperCase().split(',').join(' · ');
  const totalSize = useMemo(() => conversion.files.reduce((total, file) => total + file.size, 0), [conversion.files]);
  const selectedLabel =
    conversion.files.length > 0
      ? `${conversion.files.length} ${conversion.files.length === 1 ? 'archivo seleccionado' : 'archivos seleccionados'}`
      : 'Arrastra archivos o explora tu equipo';

  return (
    <section id="converter" aria-label="Conversor de archivos" className="scroll-mt-24">
      <Card className="h-full min-h-[620px] border-border/70 bg-card/88 shadow-2xl shadow-black/25 backdrop-blur sm:min-h-[560px]">
        <CardHeader className="border-b border-border/45 pb-5">
          <div className="space-y-1">
            <span className="text-xs font-semibold tracking-normal text-muted-foreground uppercase">Nueva conversión</span>
            <CardTitle className="text-2xl font-semibold tracking-normal sm:text-3xl">Carga tus archivos</CardTitle>
            <CardDescription>Hasta {conversion.maxBatchFiles} archivos por lote. La cola procesa uno por uno y mantiene el avance por archivo.</CardDescription>
          </div>
        </CardHeader>

        <CardContent className="grid gap-5">
          <Label
            htmlFor="conversion-file"
            className={cn(
              'group grid min-h-52 cursor-pointer place-items-center gap-3 rounded-lg border border-dashed border-border/80 bg-background/35 p-8 text-center transition-colors hover:border-primary/70 hover:bg-primary/5',
              conversion.files.length > 0 && 'border-primary/70 bg-primary/10',
            )}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              conversion.selectFiles(event.dataTransfer.files);
            }}
          >
            <Input
              id="conversion-file"
              ref={inputRef}
              className="sr-only"
              type="file"
              multiple
              accept={acceptedExtensions()}
              onChange={(event) => conversion.selectFiles(event.currentTarget.files)}
            />
            <span className="flex size-12 items-center justify-center rounded-lg bg-primary/10 text-primary ring-1 ring-primary/25">
              {conversion.files.length > 1 ? <Layers3 className="size-6" aria-hidden="true" /> : <UploadCloud className="size-6" aria-hidden="true" />}
            </span>
            <span className="max-w-full overflow-hidden text-lg font-semibold text-ellipsis text-foreground">{selectedLabel}</span>
            <span className="max-w-full text-sm text-muted-foreground">
              {conversion.files.length > 0 ? `${formatBytes(totalSize)} · ${conversion.sourceFormat ? conversion.sourceFormat.toUpperCase() : 'Formatos mixtos'}` : acceptedFormatsLabel}
            </span>
          </Label>

          {conversion.queue.length > 0 && (
            <ItemGroup className="gap-2">
              {conversion.queue.map((item, index) => (
                <Item key={item.id} variant="muted" className="border-border/60 bg-background/45">
                  <ItemMedia className="size-10 rounded-lg bg-primary/10 text-primary ring-1 ring-primary/20">
                    <FileText className="size-5" aria-hidden="true" />
                  </ItemMedia>
                  <ItemContent className="min-w-0">
                    <ItemTitle className="max-w-full">
                      <span className="truncate">{item.file.name}</span>
                      {item.job && <JobStatusBadge status={item.job.status} />}
                    </ItemTitle>
                    <ItemDescription className="truncate">
                      #{index + 1} en cola · {formatBytes(item.file.size)} · {item.sourceFormat.toUpperCase()}
                      {item.error ? ` · ${item.error}` : ''}
                    </ItemDescription>
                    {item.job && ['QUEUED', 'PROCESSING'].includes(item.job.status) && <Progress value={item.job.status === 'PROCESSING' ? 62 : 24} className="mt-1 h-1" />}
                  </ItemContent>
                  <ItemActions>
                    {item.job && <DownloadJobButton job={item.job} variant="icon" onError={conversion.setError} />}
                  </ItemActions>
                </Item>
              ))}
            </ItemGroup>
          )}

          {conversion.fileTooLarge && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>
                {conversion.oversizedFiles.length === 1 ? 'Un archivo supera' : `${conversion.oversizedFiles.length} archivos superan`} el límite configurado de {env.maxFileSizeMb} MB.
              </AlertDescription>
            </Alert>
          )}
          {conversion.mixedSourceFormats && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>El lote debe usar el mismo formato de origen para evitar conversiones ambiguas.</AlertDescription>
            </Alert>
          )}
          {conversion.files.length > 0 && conversion.sourceFormat && target.targetOptions.length === 0 && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>El formato {conversion.sourceFormat.toUpperCase()} no está disponible por ahora.</AlertDescription>
            </Alert>
          )}

          <TargetFormatGrid options={target.targetOptions} targetFormat={target.targetFormat} onSelect={target.setTargetFormat} />

          <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
            <ConvertButton
              flowState={conversion.flowState}
              fileCount={conversion.files.length}
              disabled={!conversion.canStart || !target.targetFormat}
              onClick={() => void conversion.convert(target.targetFormat)}
            />
            {conversion.queue.length > 0 && (
              <Button variant="outline" type="button" className="h-11" onClick={conversion.clearQueue}>
                <Trash2 className="size-4" aria-hidden="true" />
                Limpiar
              </Button>
            )}
          </div>

          <ConversionProgress currentJobs={conversion.currentJobs} fileCount={conversion.files.length} flowState={conversion.flowState} />

          {target.selectedPair && <ConversionRouteSummary pair={target.selectedPair} />}

          {conversion.currentJobs.length > 0 && (
            <div className="grid gap-2 rounded-lg border border-border/60 bg-background/35 p-4 sm:grid-cols-3">
              <div>
                <p className="text-xs font-medium text-muted-foreground">En proceso</p>
                <p className="text-lg font-semibold text-foreground">{conversion.activeCount}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Completados</p>
                <p className="text-lg font-semibold text-foreground">{conversion.completedCount}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Fallidos</p>
                <p className="text-lg font-semibold text-foreground">{conversion.failedCount}</p>
              </div>
            </div>
          )}

          {conversion.error && (
            <Alert variant="destructive">
              <XCircle className="size-4" aria-hidden="true" />
              <AlertDescription>{conversion.error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
