import { useMemo } from 'react';
import { Activity, CheckCircle2, Clock3, FileStack, XCircle } from 'lucide-react';
import { ConversionIcon, findConversionPair } from '../../../entities/conversion';
import type { ConversionPair } from '../../../entities/conversion';
import { isActiveJobStatus, JobStatusBadge, useJobsHistory } from '../../../entities/job';
import { cn } from '../../../shared/lib/utils';
import { formatBytes } from '../../../shared/lib/formatBytes';
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/ui/card';
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from '../../../shared/ui/empty';
import { Item, ItemContent, ItemDescription, ItemMedia, ItemTitle } from '../../../shared/ui/item';

export function ConversionOverviewWidget() {
  const jobs = useJobsHistory();

  const stats = useMemo(() => {
    const data = jobs.data ?? [];
    const total = data.length;
    const completed = data.filter((job) => job.status === 'COMPLETED').length;
    const failed = data.filter((job) => job.status === 'FAILED' || job.status === 'EXPIRED').length;
    const active = data.filter((job) => isActiveJobStatus(job.status)).length;
    const volume = data.filter((job) => job.status === 'COMPLETED').reduce((sum, job) => sum + job.file_size, 0);

    const pairCounts = new Map<string, { count: number; source: string; target: string; category?: ConversionPair['category'] }>();
    for (const job of data) {
      const key = `${job.source_format}->${job.target_format}`;
      const pair = findConversionPair(job.source_format, job.target_format);
      const entry = pairCounts.get(key) ?? { count: 0, source: job.source_format, target: job.target_format, category: pair?.category };
      entry.count += 1;
      pairCounts.set(key, entry);
    }
    const topPair = [...pairCounts.values()].sort((a, b) => b.count - a.count)[0];

    const latest = [...data].sort((a, b) => b.created_at.localeCompare(a.created_at))[0];

    return { total, completed, failed, active, volume, topPair, latest };
  }, [jobs.data]);

  const isEmpty = (jobs.data?.length ?? 0) === 0;

  return (
    <section id="overview" aria-label="Resumen de conversiones" className="scroll-mt-24">
      <Card>
        <CardHeader className="border-b-2 border-border pb-6">
          <div className="space-y-1">
            <span className="font-mono text-[0.65rem] font-black tracking-[0.16em] text-primary uppercase">Metrics / session pulse</span>
            <CardTitle className="text-3xl font-black tracking-[-0.06em] sm:text-4xl">Tu actividad.</CardTitle>
            <p className="text-base font-medium text-muted-foreground">Una lectura rápida de tus operaciones en esta sesión.</p>
          </div>
        </CardHeader>

        <CardContent className="grid gap-4 pt-6">
          {isEmpty ? (
            <Empty className="min-h-64 border-2 border-dashed border-border bg-background">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <FileStack className="size-4" aria-hidden="true" />
                </EmptyMedia>
                <EmptyTitle className="text-xl font-black tracking-[-0.04em]">Sin actividad aún</EmptyTitle>
                <EmptyDescription>Tus estadísticas aparecerán aquí cuando proceses tu primera conversión.</EmptyDescription>
              </EmptyHeader>
            </Empty>
          ) : (
            <>
              <div className="grid gap-3 sm:grid-cols-2">
                <StatTile icon={<FileStack className="size-4" aria-hidden="true" />} label="Total" value={stats.total} />
                <StatTile icon={<Activity className="size-4" aria-hidden="true" />} label="En proceso" value={stats.active} tone="accent" />
                <StatTile icon={<CheckCircle2 className="size-4" aria-hidden="true" />} label="Completados" value={stats.completed} tone="primary" />
                <StatTile icon={<XCircle className="size-4" aria-hidden="true" />} label="Fallidos" value={stats.failed} tone="destructive" />
              </div>

              <div className="grid gap-3 border-2 border-border bg-secondary p-4 sm:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Volumen procesado</p>
                  <p className="text-lg font-semibold text-foreground">{formatBytes(stats.volume)}</p>
                </div>
                {stats.topPair && (
                  <div className="space-y-1">
                    <p className="text-xs font-medium text-muted-foreground">Conversión más usada</p>
                    <p className="flex items-center gap-2 text-lg font-semibold text-foreground">
                      <ConversionIcon category={stats.topPair.category} className="size-4" />
                      {stats.topPair.source.toUpperCase()} → {stats.topPair.target.toUpperCase()}
                      <span className="text-sm font-normal text-muted-foreground">· {stats.topPair.count}x</span>
                    </p>
                  </div>
                )}
              </div>

              {stats.latest && (
                <div className="space-y-2">
                  <p className="text-xs font-semibold tracking-normal text-muted-foreground uppercase">Última conversión</p>
                  <Item variant="muted" className="p-4">
                    <ItemMedia variant="icon" className="size-11 border-2 border-border bg-foreground text-background">
                      <ConversionIcon category={findConversionPair(stats.latest.source_format, stats.latest.target_format)?.category} className="size-5" />
                    </ItemMedia>
                    <ItemContent className="min-w-0">
                      <ItemTitle className="max-w-full truncate">
                        {stats.latest.source_format.toUpperCase()} a {stats.latest.target_format.toUpperCase()}
                      </ItemTitle>
                      <ItemDescription className="max-w-full truncate">
                        <Clock3 className="mr-1 inline size-3" aria-hidden="true" />
                        {new Date(stats.latest.created_at).toLocaleString()} · {formatBytes(stats.latest.file_size)}
                      </ItemDescription>
                    </ItemContent>
                    <JobStatusBadge status={stats.latest.status} withIcon />
                  </Item>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

interface StatTileProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  tone?: 'default' | 'primary' | 'accent' | 'destructive';
}

function StatTile({ icon, label, value, tone = 'default' }: StatTileProps) {
  const toneClass: Record<NonNullable<StatTileProps['tone']>, string> = {
    default: 'bg-muted/40 text-muted-foreground ring-border/60',
    primary: 'bg-primary/10 text-primary ring-primary/25',
    accent: 'bg-accent/10 text-accent ring-accent/25',
    destructive: 'bg-destructive/10 text-destructive ring-destructive/25',
  };

  return (
    <div className="flex items-center gap-3 border-2 border-border bg-background p-4">
      <span className={cn('flex size-10 shrink-0 items-center justify-center border-2 border-border', toneClass[tone])}>{icon}</span>
      <span className="grid min-w-0">
        <span className="font-mono text-[0.65rem] font-black tracking-[0.12em] text-muted-foreground uppercase">{label}</span>
        <span className="text-3xl font-black tracking-[-0.06em] text-foreground">{value}</span>
      </span>
    </div>
  );
}
