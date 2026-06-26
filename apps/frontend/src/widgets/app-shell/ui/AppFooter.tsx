import { FileArchive } from 'lucide-react';
import { Separator } from '@/shared/ui/separator';

export function AppFooter() {
  return (
    <footer className="border-t border-border/60 bg-background/70">
      <div className="mx-auto grid w-full max-w-7xl gap-4 px-4 py-6 text-sm text-muted-foreground sm:px-6 md:grid-cols-[1fr_auto] md:items-center">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-primary ring-1 ring-border/70">
            <FileArchive className="size-4" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block truncate font-medium text-foreground">Morphix</span>
            <span className="block truncate">Documentos, imágenes, audio y video en un solo flujo.</span>
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-3 md:justify-end">
          <span>Privado por sesión</span>
          <Separator orientation="vertical" className="h-4" />
          <span>15 conversiones</span>
          <Separator orientation="vertical" className="h-4" />
          <span>Hasta 100 MB</span>
          <Separator orientation="vertical" className="h-4" />
          <span>Descarga inmediata</span>
        </div>
      </div>
    </footer>
  );
}
