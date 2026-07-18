import { useEffect, useMemo, useRef, useState, type ReactNode, type RefObject } from 'react';
import { ArrowDown, ArrowLeft, ArrowRight, FileText, RefreshCw, UploadCloud, XCircle } from 'lucide-react';
import { acceptedExtensions, ConversionRouteSummary, type ConversionPair } from '../../../entities/conversion';
import { JobStatusBadge } from '../../../entities/job';
import { ConvertButton, ConversionProgress, useConvertFile } from '../../../features/convert-file';
import { DownloadJobButton } from '../../../features/download-job-result';
import { FilePreviewButton } from '../../../features/preview-file';
import { TargetFormatGrid, useTargetFormat } from '../../../features/select-target-format';
import { env } from '../../../shared/config/env';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { Alert, AlertDescription } from '../../../shared/ui/alert';
import { Button } from '../../../shared/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/ui/card';
import { Input } from '../../../shared/ui/input';
import { Item, ItemActions, ItemContent, ItemDescription, ItemGroup, ItemMedia, ItemTitle } from '../../../shared/ui/item';
import { Label } from '../../../shared/ui/label';
import { Progress } from '../../../shared/ui/progress';

type WorkspacePhase = 'upload' | 'format' | 'review' | 'progress';

export function ConversionWorkspace() {
  const inputRef = useRef<HTMLInputElement>(null);
  const conversion = useConvertFile();
  const target = useTargetFormat(conversion.sourceFormat);
  const [phase, setPhase] = useState<WorkspacePhase>('upload');
  const totalSize = useMemo(() => conversion.files.reduce((total, file) => total + file.size, 0), [conversion.files]);
  const acceptedFormatsLabel = acceptedExtensions().replaceAll('.', '').toUpperCase().split(',').join(' · ');
  const hasSelectionErrors = conversion.fileTooLarge || conversion.mixedSourceFormats || (Boolean(conversion.sourceFormat) && target.targetOptions.length === 0);

  useEffect(() => {
    if (conversion.queue.length === 0) setPhase('upload');
  }, [conversion.queue.length]);

  useEffect(() => {
    if (conversion.currentJobs.length > 0 && ['polling', 'ready', 'failed'].includes(conversion.flowState)) setPhase('progress');
  }, [conversion.currentJobs.length, conversion.flowState]);

  function selectFiles(fileList: FileList | File[] | null) {
    const files = Array.from(fileList ?? []);
    conversion.selectFiles(fileList);
    if (files.length > 0) setPhase('format');
  }

  function clearQueue() {
    conversion.clearQueue();
    if (inputRef.current) inputRef.current.value = '';
    setPhase('upload');
  }

  function changeFiles() {
    clearQueue();
    requestAnimationFrame(() => inputRef.current?.click());
  }

  function startConversion() {
    setPhase('progress');
    void conversion.convert(target.targetFormat);
  }

  return (
    <section id="converter" aria-label="Conversor de archivos">
      <Card>
        <CardHeader className="border-b-2 border-border pb-6">
          <div className="flex items-start justify-between gap-4">
            <div className="grid min-w-0 gap-2">
              <span className="font-mono text-[0.65rem] font-black tracking-[0.16em] text-primary uppercase">{phaseLabel[phase]}</span>
              <CardTitle className="text-3xl font-black tracking-[-0.06em] sm:text-5xl">{phaseTitle[phase]}</CardTitle>
              <p className="max-w-2xl text-base font-medium leading-relaxed text-muted-foreground">{phase === 'format' && conversion.files.length > 1 ? 'Selecciona el resultado que necesitas. Solo mostramos opciones compatibles con tus archivos.' : phaseDescription[phase]}</p>
            </div>
            {phase !== 'upload' && <span className="hidden shrink-0 border-2 border-border bg-secondary px-3 py-1 font-mono text-[0.65rem] font-black tracking-[0.1em] uppercase sm:inline">{conversion.files.length} {conversion.files.length === 1 ? 'archivo' : 'archivos'}</span>}
          </div>
        </CardHeader>

        <CardContent className="grid gap-6 pt-7">
          {phase === 'upload' && <UploadPhase inputRef={inputRef} acceptedFormatsLabel={acceptedFormatsLabel} onSelect={selectFiles} />}

          {phase === 'format' && (
            <FormatPhase
              sourceFormat={conversion.sourceFormat}
              fileCount={conversion.files.length}
              totalSize={totalSize}
              options={target.targetOptions}
              targetFormat={target.targetFormat}
              onSelect={target.setTargetFormat}
              onChangeFiles={changeFiles}
              errors={<SelectionErrors conversion={conversion} hasSelectionErrors={hasSelectionErrors} targetOptionsLength={target.targetOptions.length} />}
            />
          )}

          {phase === 'review' && <ReviewPhase files={conversion.files} sourceFormat={conversion.sourceFormat} targetPair={target.selectedPair} totalSize={totalSize} onBack={() => setPhase('format')} />}

          {phase === 'progress' && <ProgressPhase conversion={conversion} onNewConversion={clearQueue} />}

          {conversion.error && <Alert variant="destructive"><XCircle className="size-4" aria-hidden="true" /><AlertDescription>{conversion.error}</AlertDescription></Alert>}

          {phase === 'format' && (
            <div className="flex flex-col-reverse gap-3 border-t-2 border-border pt-6 sm:flex-row sm:justify-between">
              <Button variant="ghost" type="button" onClick={clearQueue}><ArrowLeft className="size-4" aria-hidden="true" /> Cambiar archivos</Button>
              <Button type="button" disabled={!conversion.canStart || !target.targetFormat || hasSelectionErrors} onClick={() => setPhase('review')}><span>Revisar conversión</span><ArrowRight className="size-4" aria-hidden="true" /></Button>
            </div>
          )}

          {phase === 'review' && (
            <div className="grid gap-3 border-t-2 border-border pt-6 sm:grid-cols-[auto_minmax(0,1fr)] sm:items-center sm:gap-5">
              <Button variant="ghost" type="button" onClick={() => setPhase('format')}><ArrowLeft className="size-4" aria-hidden="true" /> Atrás</Button>
              <div className="min-w-0"><ConvertButton flowState={conversion.flowState} fileCount={conversion.files.length} disabled={!conversion.canStart || !target.targetFormat} onClick={startConversion} /></div>
            </div>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

const phaseLabel: Record<WorkspacePhase, string> = { upload: 'Nueva conversión', format: 'Formato de salida', review: 'Confirmación', progress: 'Resultado' };
const phaseTitle: Record<WorkspacePhase, string> = { upload: 'Carga tus archivos.', format: 'Elige el formato final.', review: 'Revisa antes de convertir.', progress: 'Tu conversión está en marcha.' };
const phaseDescription: Record<WorkspacePhase, string> = {
  upload: 'Suelta tus archivos o selecciónalos desde tu equipo. Puedes cargar hasta 10 archivos del mismo formato.',
  format: 'Selecciona el resultado que necesitas. Solo mostramos opciones compatibles con tu archivo.',
  review: 'Confirma los archivos y la ruta de salida. Podrás descargar cada resultado cuando termine.',
  progress: 'La cola trabaja en segundo plano y actualiza el estado de cada archivo automáticamente.',
};

function UploadPhase({ inputRef, acceptedFormatsLabel, onSelect }: { inputRef: RefObject<HTMLInputElement | null>; acceptedFormatsLabel: string; onSelect: (fileList: FileList | null) => void }) {
  return (
    <Label htmlFor="conversion-file" className="group grid min-h-72 cursor-pointer place-items-center gap-4 border-2 border-dashed border-border bg-background p-8 text-center transition-colors hover:bg-accent sm:min-h-80" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); onSelect(event.dataTransfer.files); }}>
      <Input id="conversion-file" ref={inputRef} className="sr-only" type="file" multiple accept={acceptedExtensions()} onChange={(event) => onSelect(event.currentTarget.files)} />
      <span className="flex size-14 items-center justify-center border-2 border-foreground bg-primary text-primary-foreground shadow-[5px_5px_0_var(--shadow)] transition-transform group-hover:translate-x-1 group-hover:translate-y-1 group-hover:shadow-[2px_2px_0_var(--shadow)]"><UploadCloud className="size-7" aria-hidden="true" /></span>
      <span className="max-w-full text-2xl font-black tracking-[-0.05em]">Suelta tus archivos aquí</span>
      <span className="max-w-full font-mono text-[0.68rem] font-bold tracking-[0.12em] text-foreground uppercase">{acceptedFormatsLabel}</span>
      <span className="inline-flex items-center gap-1 font-mono text-[0.65rem] font-black tracking-[0.12em] uppercase">Explorar equipo <ArrowDown className="size-3" aria-hidden="true" /></span>
    </Label>
  );
}

function FormatPhase({ sourceFormat, fileCount, totalSize, options, targetFormat, onSelect, onChangeFiles, errors }: { sourceFormat: string; fileCount: number; totalSize: number; options: ConversionPair[]; targetFormat: string; onSelect: (targetFormat: string) => void; onChangeFiles: () => void; errors: ReactNode }) {
  return (
    <div className="grid gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3 border-2 border-border bg-secondary p-4">
        <div className="flex min-w-0 items-center gap-3"><span className="flex size-10 items-center justify-center border-2 border-border bg-foreground text-background"><FileText className="size-5" aria-hidden="true" /></span><span className="grid min-w-0 gap-1"><span className="font-mono text-sm font-black tracking-[0.14em] uppercase">{sourceFormat.toUpperCase()}</span><span className="font-mono text-[0.65rem] font-bold tracking-[0.1em] text-muted-foreground uppercase">{formatBytes(totalSize)} · {fileCount === 1 ? 'Archivo listo' : 'Archivos listos'}</span></span></div>
        <Button variant="outline" size="sm" type="button" onClick={onChangeFiles}><RefreshCw className="size-3" aria-hidden="true" /> Cambiar</Button>
      </div>
      {errors}
      {options.length > 0 && <TargetFormatGrid options={options} targetFormat={targetFormat} onSelect={onSelect} />}
    </div>
  );
}

function SelectionErrors({ conversion, hasSelectionErrors, targetOptionsLength }: { conversion: ReturnType<typeof useConvertFile>; hasSelectionErrors: boolean; targetOptionsLength: number }) {
  if (!hasSelectionErrors) return null;
  return <div className="grid gap-2">{conversion.fileTooLarge && <Alert variant="destructive"><XCircle className="size-4" aria-hidden="true" /><AlertDescription>{conversion.oversizedFiles.length === 1 ? 'Un archivo supera' : `${conversion.oversizedFiles.length} archivos superan`} el límite de {env.maxFileSizeMb} MB.</AlertDescription></Alert>}{conversion.mixedSourceFormats && <Alert variant="destructive"><XCircle className="size-4" aria-hidden="true" /><AlertDescription>El lote debe usar el mismo formato de origen.</AlertDescription></Alert>}{conversion.sourceFormat && targetOptionsLength === 0 && <Alert variant="destructive"><XCircle className="size-4" aria-hidden="true" /><AlertDescription>Este formato de origen no está disponible por ahora.</AlertDescription></Alert>}</div>;
}

function ReviewPhase({ files, sourceFormat, targetPair, totalSize, onBack }: { files: File[]; sourceFormat: string; targetPair?: ConversionPair; totalSize: number; onBack: () => void }) {
  return (
    <div className="grid gap-5">
      <div className="grid gap-3 border-2 border-border bg-secondary p-5 sm:grid-cols-3"><SummaryCell label="Archivos" value={`${files.length}`} /><SummaryCell label="Origen" value={sourceFormat.toUpperCase()} /><SummaryCell label="Tamaño total" value={formatBytes(totalSize)} /></div>
      <div className="grid gap-2"><span className="font-mono text-[0.65rem] font-black tracking-[0.15em] text-muted-foreground uppercase">Archivos seleccionados</span><ItemGroup className="gap-2">{files.map((file) => <Item key={`${file.name}-${file.size}`} variant="muted" className="p-3"><ItemMedia className="size-9 border-2 border-border bg-foreground text-background"><FileText className="size-4" aria-hidden="true" /></ItemMedia><ItemContent className="min-w-0"><ItemTitle className="truncate font-black">{file.name}</ItemTitle><ItemDescription className="font-mono text-[0.65rem] uppercase">{formatBytes(file.size)}</ItemDescription></ItemContent><ItemActions><FilePreviewButton file={file} /></ItemActions></Item>)}</ItemGroup></div>
      {targetPair && <ConversionRouteSummary pair={targetPair} />}
    </div>
  );
}

function ProgressPhase({ conversion, onNewConversion }: { conversion: ReturnType<typeof useConvertFile>; onNewConversion: () => void }) {
  return (
    <div className="grid gap-6"><ConversionProgress currentJobs={conversion.currentJobs} fileCount={conversion.files.length} flowState={conversion.flowState} /><ItemGroup className="gap-3">{conversion.queue.map((item, index) => <Item key={item.id} variant="muted" className="gap-3 p-4"><ItemMedia className="size-10 border-2 border-border bg-foreground text-background"><FileText className="size-5" aria-hidden="true" /></ItemMedia><ItemContent className="min-w-0 gap-2"><ItemTitle className="max-w-full justify-between gap-2 font-black"><span className="truncate">{item.file.name}</span>{item.job && <JobStatusBadge status={item.job.status} />}</ItemTitle><ItemDescription className="truncate font-mono text-[0.65rem] uppercase">#{index + 1} · {formatBytes(item.file.size)}{item.job?.progress_stage ? ` · ${item.job.progress_stage}` : ''}{item.error ? ` · ${item.error}` : ''}</ItemDescription>{item.job && <Progress value={item.job.progress_percent ?? (item.job.status === 'COMPLETED' || item.job.status === 'FAILED' ? 100 : item.job.status === 'PROCESSING' ? 62 : 24)} className="h-2" />}</ItemContent><ItemActions><FilePreviewButton file={item.file} />{item.job && <DownloadJobButton job={item.job} variant="icon" onError={conversion.setError} />}</ItemActions></Item>)}</ItemGroup><div className="flex justify-end border-t-2 border-border pt-5"><Button variant="outline" type="button" onClick={onNewConversion}><RefreshCw className="size-4" aria-hidden="true" /> Nueva conversión</Button></div></div>
  );
}

function SummaryCell({ label, value }: { label: string; value: string }) {
  return <div className="grid gap-1"><span className="font-mono text-[0.65rem] font-black tracking-[0.12em] text-muted-foreground uppercase">{label}</span><span className="text-2xl font-black tracking-[-0.05em]">{value}</span></div>;
}
