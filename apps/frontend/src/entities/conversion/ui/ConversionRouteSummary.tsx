import type { ConversionPair } from '../model/conversionTypes';
import { Badge } from '../../../shared/ui/badge';
import { Item, ItemContent, ItemDescription, ItemMedia, ItemTitle } from '../../../shared/ui/item';
import { ConversionIcon } from './ConversionIcon';

interface ConversionRouteSummaryProps {
  pair: ConversionPair;
}

export function ConversionRouteSummary({ pair }: ConversionRouteSummaryProps) {
  return (
    <Item variant="muted" className="border-border/60 bg-primary/10">
      <ItemMedia variant="icon" className="text-primary">
        <ConversionIcon category={pair.category} className="size-5" />
      </ItemMedia>
      <ItemContent>
        <ItemTitle>{pair.label}</ItemTitle>
        <ItemDescription>{pair.engine} en worker ECS Fargate</ItemDescription>
      </ItemContent>
      <Badge variant="outline" className="border-primary/35 text-primary">
        Ruta
      </Badge>
    </Item>
  );
}
