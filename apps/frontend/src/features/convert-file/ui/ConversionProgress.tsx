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
  const progressSteps = [
    { key: 'creating', label: fileCount > 1 ? 'Archivos' : 'Archivo', active: flowState === 'creating', done: hasJobs },
    { key: 'uploading', label: 'Carga', active: flowState === 'uploading', done: ['starting', 'polling', 'ready'].includes(flowState) },
    { key: 'polling', label: 'Conversión', active: ['starting', 'polling'].includes(flowState), done: hasJobs && finishedCount === currentJobs.length, value: realtimeProgress },
    { key: 'ready', label: 'Resultado', active: flowState === 'ready', done: flowState === 'ready' },
  ];

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-4" aria-label="Conversion progress">
      {progressSteps.map((step) => (
        <div key={step.key} className="grid gap-2">
          <Progress value={step.done ? 100 : step.active ? step.value ?? 62 : 0} className="h-1.5" />
          <span className="text-xs text-muted-foreground">{step.label}</span>
        </div>
      ))}
    </div>
  );
}
