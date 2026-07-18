import { useEffect, useMemo, useState } from 'react';
import { AudioLines, Eye, FileText, Image as ImageIcon, Loader2, MonitorPlay, X } from 'lucide-react';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { Button } from '../../../shared/ui/button';
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../../../shared/ui/dialog';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../../shared/ui/tooltip';

type PreviewKind = 'image' | 'pdf' | 'text' | 'audio' | 'video' | 'unsupported';

interface FilePreviewButtonProps {
  file: File;
}

export function FilePreviewButton({ file }: FilePreviewButtonProps) {
  const [open, setOpen] = useState(false);
  const kind = useMemo(() => getPreviewKind(file), [file]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant="outline" size="icon" type="button" aria-label={`Visualizar ${file.name}`} onClick={() => setOpen(true)}>
            <Eye className="size-4" aria-hidden="true" />
          </Button>
        </TooltipTrigger>
        <TooltipContent>Vista previa</TooltipContent>
      </Tooltip>

      <DialogContent className="sm:max-w-4xl">
        <DialogHeader className="pr-8">
          <div className="mb-2 flex size-11 items-center justify-center border-2 border-border bg-primary text-primary-foreground">
            <PreviewIcon kind={kind} />
          </div>
          <DialogTitle className="break-words">{file.name}</DialogTitle>
          <DialogDescription>{formatBytes(file.size)} · {file.type || 'Formato de archivo'}</DialogDescription>
        </DialogHeader>

        <PreviewSurface file={file} kind={kind} />

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" type="button"><X className="size-4" aria-hidden="true" /> Cerrar</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function PreviewSurface({ file, kind }: { file: File; kind: PreviewKind }) {
  const [objectUrl, setObjectUrl] = useState('');
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(kind === 'text');

  useEffect(() => {
    if (kind === 'unsupported' || kind === 'text') return;

    const url = URL.createObjectURL(file);
    setObjectUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file, kind]);

  useEffect(() => {
    if (kind !== 'text') return;

    let cancelled = false;
    setLoading(true);
    void file.text().then((content) => {
      if (cancelled) return;
      setText(content);
      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [file, kind]);

  if (kind === 'image') {
    return <div className="grid min-h-80 place-items-center border-2 border-border bg-secondary p-4"><img src={objectUrl} alt={`Vista previa de ${file.name}`} className="max-h-[60vh] max-w-full border-2 border-border object-contain shadow-[5px_5px_0_var(--shadow)]" /></div>;
  }

  if (kind === 'pdf') {
    return <iframe src={objectUrl} title={`Vista previa de ${file.name}`} className="h-[60vh] min-h-[420px] w-full border-2 border-border bg-white" />;
  }

  if (kind === 'audio') {
    return <div className="grid min-h-80 place-items-center border-2 border-border bg-secondary p-8"><div className="grid w-full max-w-xl gap-5 border-2 border-border bg-card p-6 shadow-[5px_5px_0_var(--shadow)]"><AudioLines className="size-10 text-primary" aria-hidden="true" /><audio controls src={objectUrl} className="w-full" /></div></div>;
  }

  if (kind === 'video') {
    return <div className="grid min-h-80 place-items-center border-2 border-border bg-secondary p-4"><video controls src={objectUrl} className="max-h-[60vh] max-w-full border-2 border-border bg-black shadow-[5px_5px_0_var(--shadow)]" /></div>;
  }

  if (kind === 'text') {
    return <div className="relative min-h-80 border-2 border-border bg-secondary p-4">{loading ? <div className="grid min-h-72 place-items-center"><Loader2 className="size-6 animate-spin text-primary" aria-label="Cargando vista previa" /></div> : <pre className="max-h-[60vh] overflow-auto whitespace-pre-wrap border-2 border-border bg-card p-5 font-mono text-sm leading-relaxed text-foreground">{text}</pre>}</div>;
  }

  return <div className="grid min-h-80 place-items-center border-2 border-border bg-secondary p-8 text-center"><div className="grid max-w-md gap-3"><FileText className="mx-auto size-10 text-primary" aria-hidden="true" /><p className="text-xl font-black tracking-[-0.04em]">Vista previa no disponible</p><p className="font-medium text-muted-foreground">Este formato se puede convertir, pero el navegador no puede mostrarlo directamente.</p></div></div>;
}

function getPreviewKind(file: File): PreviewKind {
  const extension = file.name.split('.').pop()?.toLowerCase();
  const type = file.type.toLowerCase();

  if (type.startsWith('image/')) return 'image';
  if (type === 'application/pdf' || extension === 'pdf') return 'pdf';
  if (type.startsWith('audio/')) return 'audio';
  if (type.startsWith('video/')) return 'video';
  if (type.startsWith('text/') || extension === 'csv' || extension === 'txt') return 'text';
  return 'unsupported';
}

function PreviewIcon({ kind }: { kind: PreviewKind }) {
  if (kind === 'image') return <ImageIcon className="size-5" aria-hidden="true" />;
  if (kind === 'audio') return <AudioLines className="size-5" aria-hidden="true" />;
  if (kind === 'video') return <MonitorPlay className="size-5" aria-hidden="true" />;
  return <FileText className="size-5" aria-hidden="true" />;
}
