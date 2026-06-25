import type { JobRecord } from '../../../entities/job';
import { Progress } from '../../../shared/ui/progress';
import type { FlowState } from '../model/convertFileTypes';

interface ConversionProgressProps {
  currentJobs: JobRecord[];
  flowState: FlowState;
  fileCount: number;
}

export function ConversionProgress({ currentJobs, flowState, fileCount }: ConversionProgressProps) {
  const hasJobs = currentJobs.length > 0;
  const finishedCount = currentJobs.filter((job) => ['COMPLETED', 'FAILED', 'EXPIRED', 'DELETED'].includes(job.status)).length;
  const progressSteps = [
    { key: 'creating', label: fileCount > 1 ? 'Archivos' : 'Archivo', active: flowState === 'creating', done: hasJobs },
    { key: 'uploading', label: 'Carga', active: flowState === 'uploading', done: ['starting', 'polling', 'ready'].includes(flowState) },
    { key: 'polling', label: 'Cola', active: ['starting', 'polling'].includes(flowState), done: hasJobs && finishedCount === currentJobs.length },
    { key: 'ready', label: 'Resultado', active: flowState === 'ready', done: flowState === 'ready' },
  ];

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-4" aria-label="Conversion progress">
      {progressSteps.map((step) => (
        <div key={step.key} className="grid gap-2">
          <Progress value={step.done ? 100 : step.active ? 62 : 0} className="h-1.5" />
          <span className="text-xs text-muted-foreground">{step.label}</span>
        </div>
      ))}
    </div>
  );
}
