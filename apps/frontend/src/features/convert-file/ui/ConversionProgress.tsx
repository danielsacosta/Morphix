import type { JobRecord } from '../../../entities/job';
import { Progress } from '../../../shared/ui/progress';
import type { FlowState } from '../model/convertFileTypes';

interface ConversionProgressProps {
  currentJobs: JobRecord[];
  flowState: FlowState;
  fileCount: number;
}

function fallbackProgress(job: JobRecord): number {
  if (job.status === 'COMPLETED' || job.status === 'FAILED') return 100;
  if (job.status === 'PROCESSING') return 60;
  if (job.status === 'QUEUED') return 10;
  if (job.status === 'UPLOADED') return 8;
  return 0;
}

export function ConversionProgress({ currentJobs, flowState, fileCount }: ConversionProgressProps) {
  const hasJobs = currentJobs.length > 0;
  const finishedCount = currentJobs.filter((job) => ['COMPLETED', 'FAILED', 'EXPIRED', 'DELETED'].includes(job.status)).length;
  const realtimeProgress = hasJobs ? currentJobs.reduce((total, job) => total + (job.progress_percent ?? fallbackProgress(job)), 0) / currentJobs.length : 0;
  const label = flowState === 'ready' ? 'Conversión completada' : flowState === 'failed' ? 'La conversión necesita atención' : flowState === 'polling' ? 'Procesando archivos' : fileCount > 1 ? 'Preparando archivos' : 'Preparando archivo';
  const value = flowState === 'ready' ? 100 : realtimeProgress;

  return (
    <div className="grid gap-2 border-t-2 border-border pt-5" aria-label="Progreso de conversión">
      <div className="flex items-center justify-between gap-3"><span className="font-mono text-[0.65rem] font-black tracking-[0.12em] text-muted-foreground uppercase">{label}</span><span className="font-mono text-[0.65rem] font-black tracking-[0.12em] uppercase">{finishedCount}/{currentJobs.length || fileCount}</span></div>
      <Progress value={value} className="h-2" />
    </div>
  );
}
