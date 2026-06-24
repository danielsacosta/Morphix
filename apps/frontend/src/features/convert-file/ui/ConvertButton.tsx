import { Loader2, RefreshCw } from 'lucide-react';
import { Button } from '../../../shared/ui/button';
import { busyFlowStates, type FlowState } from '../model/convertFileTypes';

interface ConvertButtonProps {
  disabled: boolean;
  flowState: FlowState;
  onClick: () => void;
}

export function ConvertButton({ disabled, flowState, onClick }: ConvertButtonProps) {
  const busy = busyFlowStates.includes(flowState);

  return (
    <Button className="h-11 w-full text-sm font-semibold" size="lg" type="button" disabled={disabled} onClick={onClick}>
      {busy ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <RefreshCw className="size-4" aria-hidden="true" />}
      <span>{flowState === 'polling' ? 'Procesando' : 'Iniciar conversion'}</span>
    </Button>
  );
}
