import type { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useJobRealtime } from '../../entities/job';
import { TooltipProvider } from '../../shared/ui/tooltip';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

interface AppProvidersProps {
  children: ReactNode;
}

function RealtimeBridge() {
  useJobRealtime();
  return null;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <RealtimeBridge />
        {children}
      </TooltipProvider>
    </QueryClientProvider>
  );
}
