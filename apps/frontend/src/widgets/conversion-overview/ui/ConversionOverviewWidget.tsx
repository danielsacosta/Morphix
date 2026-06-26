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
      <Card className="h-full min-h-[620px] border-border/70 bg-card/85 shadow-2xl shadow-black/20 backdrop-blur sm:min-h-[560px]">
        <CardHeader className="border-b border-border/45 pb-5">
          <div className="space-y-1">
            <span className="text-xs font-semibold tracking-normal text-muted-foreground uppercase">Resumen</span>
            <CardTitle className="text-2xl font-semibold tracking-normal sm:text-3xl">Tu actividad</CardTitle>
          </div>
        </CardHeader>

        <CardContent className="grid flex-1 min-h-0 gap-4 overflow-y-auto">
          {isEmpty ? (
            <Empty className="min-h-32 border border-dashed border-border/70 bg-background/25">
              <EmptyHeader>
                <EmptyMedia variant="icon">
                  <FileStack className="size-4" aria-hidden="true" />
                </EmptyMedia>
                <EmptyTitle>Sin actividad aún</EmptyTitle>
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

              <div className="grid gap-3 rounded-lg border border-border/60 bg-background/35 p-4 sm:grid-cols-2">
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
                  <Item variant="muted" className="border-border/60 bg-background/35">
                    <ItemMedia variant="icon" className="size-10 rounded-lg bg-primary/10 text-primary ring-1 ring-primary/20">
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
    <div className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/35 p-4">
      <span className={cn('flex size-9 shrink-0 items-center justify-center rounded-lg ring-1', toneClass[tone])}>{icon}</span>
      <span className="grid min-w-0">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span className="text-lg font-semibold text-foreground">{value}</span>
      </span>
    </div>
  );
}
