import { FileArchive, ShieldCheck } from 'lucide-react';
import { Badge } from '@/shared/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Item, ItemContent, ItemDescription, ItemGroup, ItemMedia, ItemTitle } from '@/shared/ui/item';

const metrics = [
  { value: '15', label: 'pares MVP' },
  { value: '100 MB', label: 'limite inicial' },
  { value: 'S3', label: 'upload directo' },
  { value: 'ECS', label: 'worker aislado' },
];

const engines = ['LibreOffice', 'FFmpeg', 'ImageMagick', 'PyMuPDF'];

export function ConversionOverview() {
  return (
    <aside aria-label="Morphix overview">
      <Card className="h-full min-h-[620px] border-border/70 bg-card/85 shadow-2xl shadow-black/25 backdrop-blur sm:min-h-[560px]">
        <CardHeader className="gap-5">
          <div className="flex items-start gap-4">
            <div className="flex size-14 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <FileArchive className="size-6" aria-hidden="true" />
            </div>
            <div className="min-w-0 space-y-3">
              <Badge variant="outline" className="border-primary/35 bg-primary/10 text-primary">
                Morphix
              </Badge>
              <CardTitle className="max-w-[13ch] text-4xl leading-none font-semibold tracking-normal text-balance sm:text-5xl lg:text-6xl">
                Conversion asincrona de archivos
              </CardTitle>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex flex-1 flex-col justify-between gap-7">
          <ItemGroup className="grid grid-cols-2 gap-3" aria-label="Supported conversion coverage">
            {metrics.map((metric) => (
              <Item key={metric.label} variant="muted" className="min-h-24 flex-col items-start justify-center border-border/50 bg-muted/45">
                <ItemContent>
                  <ItemTitle className="text-2xl leading-none font-semibold text-foreground">{metric.value}</ItemTitle>
                  <ItemDescription>{metric.label}</ItemDescription>
                </ItemContent>
              </Item>
            ))}
          </ItemGroup>

          <ItemGroup className="gap-2" aria-label="Conversion engines">
            {engines.map((engine) => (
              <Item key={engine} variant="default" size="sm" className="border-border/45 bg-background/30">
                <ItemMedia variant="icon" className="text-primary">
                  <ShieldCheck className="size-4" aria-hidden="true" />
                </ItemMedia>
                <ItemContent>
                  <ItemTitle>{engine}</ItemTitle>
                </ItemContent>
              </Item>
            ))}
          </ItemGroup>
        </CardContent>
      </Card>
    </aside>
  );
}
