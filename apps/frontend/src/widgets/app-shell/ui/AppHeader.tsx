import { FileArchive } from 'lucide-react';

export function AppHeader() {
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
      </div>
    </header>
  );
}
