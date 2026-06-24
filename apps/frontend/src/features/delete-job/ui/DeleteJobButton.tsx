import { Loader2, Trash2 } from 'lucide-react';
import { Button } from '../../../shared/ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../../shared/ui/tooltip';
import { useDeleteJob } from '../model/useDeleteJob';

interface DeleteJobButtonProps {
  jobId: string;
  onDeleted?: (jobId: string) => void;
  onError?: (message: string) => void;
}

export function DeleteJobButton({ jobId, onDeleted, onError }: DeleteJobButtonProps) {
  const deletion = useDeleteJob(onDeleted, onError);

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="destructive"
          size="icon"
          type="button"
          onClick={() => deletion.mutate(jobId)}
          disabled={deletion.isPending}
          aria-label="Eliminar job"
        >
          {deletion.isPending ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <Trash2 className="size-4" aria-hidden="true" />}
        </Button>
      </TooltipTrigger>
      <TooltipContent>Eliminar job</TooltipContent>
    </Tooltip>
  );
}
