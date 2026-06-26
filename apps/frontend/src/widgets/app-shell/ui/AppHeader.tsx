import { FileArchive, BarChart3, Clock3, FileUp } from 'lucide-react';
import { Button } from '@/shared/ui/button';

type PanelView = 'history' | 'overview';

interface AppHeaderProps {
  activeView: PanelView;
  onViewChange: (view: PanelView) => void;
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

export function AppHeader({ activeView, onViewChange }: AppHeaderProps) {
  const selectView = (view: PanelView) => {
    onViewChange(view);
    if (window.innerWidth < 1024) scrollTo('panel');
  };

  return (
    <header className="sticky top-0 z-20 border-b border-border/60 bg-background/85 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <a href="#top" className="flex min-w-0 items-center gap-3 rounded-lg outline-none focus-visible:ring-3 focus-visible:ring-ring/50">
          <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <FileArchive className="size-5" aria-hidden="true" />
          </span>
          <span className="grid min-w-0">
            <span className="truncate text-base font-semibold leading-none text-foreground">Morphix</span>
            <span className="truncate text-xs text-muted-foreground">Conversor profesional de archivos</span>
          </span>
        </a>

        <nav className="flex items-center gap-1" aria-label="Navegación principal">
          <Button variant="ghost" type="button" size="sm" className="hidden sm:inline-flex" onClick={() => scrollTo('converter')}>
            <FileUp className="size-4" aria-hidden="true" />
            Convertir
          </Button>
          <Button
            variant={activeView === 'history' ? 'secondary' : 'ghost'}
            type="button"
            size="sm"
            aria-pressed={activeView === 'history'}
            onClick={() => selectView('history')}
          >
            <Clock3 className="size-4" aria-hidden="true" />
            <span className="hidden sm:inline">Historial</span>
          </Button>
          <Button
            variant={activeView === 'overview' ? 'secondary' : 'ghost'}
            type="button"
            size="sm"
            aria-pressed={activeView === 'overview'}
            onClick={() => selectView('overview')}
          >
            <BarChart3 className="size-4" aria-hidden="true" />
            <span className="hidden sm:inline">Resumen</span>
          </Button>
        </nav>
      </div>
    </header>
  );
}
