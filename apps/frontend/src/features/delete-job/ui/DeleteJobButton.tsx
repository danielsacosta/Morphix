import { useState } from 'react';
import { Loader2, Trash2, TriangleAlert } from 'lucide-react';
import { Button } from '../../../shared/ui/button';
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../shared/ui/dialog';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../../shared/ui/tooltip';
import { useDeleteJob } from '../model/useDeleteJob';

interface DeleteJobButtonProps {
  jobId: string;
  onDeleted?: (jobId: string) => void;
  onError?: (message: string) => void;
}

export function DeleteJobButton({ jobId, onDeleted, onError }: DeleteJobButtonProps) {
  const [open, setOpen] = useState(false);
  const deletion = useDeleteJob(onDeleted, onError);

  return (
    <Dialog open={open} onOpenChange={(nextOpen) => !deletion.isPending && setOpen(nextOpen)}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant="destructive"
            size="icon"
            type="button"
            onClick={() => setOpen(true)}
            disabled={deletion.isPending}
            aria-label="Eliminar conversión"
          >
            {deletion.isPending ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <Trash2 className="size-4" aria-hidden="true" />}
          </Button>
        </TooltipTrigger>
        <TooltipContent>Eliminar conversión</TooltipContent>
      </Tooltip>

      <DialogContent className="sm:max-w-md">
        <DialogHeader className="pr-8">
          <div className="mb-2 flex size-11 items-center justify-center border-2 border-border bg-destructive text-white">
            <TriangleAlert className="size-5" aria-hidden="true" />
          </div>
          <DialogTitle>Eliminar conversión</DialogTitle>
          <DialogDescription>Esta conversión se quitará del historial y dejará de estar disponible en la lista.</DialogDescription>
        </DialogHeader>

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" type="button" disabled={deletion.isPending}>
              Cancelar
            </Button>
          </DialogClose>
          <Button
            variant="destructive"
            type="button"
            onClick={() => deletion.mutate(jobId, { onSuccess: () => setOpen(false) })}
            disabled={deletion.isPending}
          >
            {deletion.isPending ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <Trash2 className="size-4" aria-hidden="true" />}
            Eliminar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
