import { FileArchive } from 'lucide-react';

export function AppFooter() {
  return (
    <footer className="border-t-2 border-border bg-foreground text-background dark:bg-card dark:text-foreground">
      <div className="mx-auto grid w-full max-w-none gap-4 px-4 py-6 text-sm sm:px-6 md:grid-cols-[1fr_auto] md:items-center lg:px-8">
        <div className="flex min-w-0 items-center gap-3">
          <span className="flex size-8 shrink-0 items-center justify-center border-2 border-background bg-primary text-primary-foreground">
            <FileArchive className="size-4" aria-hidden="true" />
          </span>
          <span className="min-w-0">
            <span className="block truncate font-black tracking-[-0.02em]">Morphix</span>
            <span className="block truncate text-background/65 dark:text-foreground/65">Documentos, imágenes, audio y video en un solo flujo.</span>
          </span>
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[0.68rem] font-bold tracking-[0.12em] text-background/65 uppercase dark:text-foreground/65 md:justify-end">
          <span>Privado por sesión</span>
          <span>Hasta 100 MB</span>
          <span>Descarga inmediata</span>
        </div>
      </div>
    </footer>
  );
}
