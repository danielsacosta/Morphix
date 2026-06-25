import { Loader2, RefreshCw } from 'lucide-react';
import { Button } from '../../../shared/ui/button';
import { busyFlowStates, type FlowState } from '../model/convertFileTypes';

interface ConvertButtonProps {
  disabled: boolean;
  flowState: FlowState;
  fileCount?: number;
  onClick: () => void;
}

export function ConvertButton({ disabled, flowState, fileCount = 0, onClick }: ConvertButtonProps) {
  const busy = busyFlowStates.includes(flowState);
  const idleLabel = fileCount > 1 ? `Encolar ${fileCount} archivos` : 'Iniciar conversión';

  return (
    <Button className="h-11 w-full text-sm font-semibold" size="lg" type="button" disabled={disabled} onClick={onClick}>
      {busy ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="size-4" aria-hidden="true" />}
      <span>{flowState === 'polling' ? 'Procesando cola' : idleLabel}</span>
    </Button>
  );
}
