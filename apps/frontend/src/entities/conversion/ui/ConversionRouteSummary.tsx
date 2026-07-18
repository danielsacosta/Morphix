import type { ConversionPair } from '../model/conversionTypes';
import { Badge } from '../../../shared/ui/badge';
import { Item, ItemContent, ItemDescription, ItemMedia, ItemTitle } from '../../../shared/ui/item';
import { ConversionIcon } from './ConversionIcon';

interface ConversionRouteSummaryProps {
  pair: ConversionPair;
}

export function ConversionRouteSummary({ pair }: ConversionRouteSummaryProps) {
  return (
    <Item variant="muted" className="border-foreground bg-accent">
      <ItemMedia variant="icon" className="size-10 border-2 border-border bg-foreground text-background">
        <ConversionIcon category={pair.category} className="size-5" />
      </ItemMedia>
      <ItemContent>
        <ItemTitle className="font-black">{pair.label}</ItemTitle>
        <ItemDescription>{pair.description}</ItemDescription>
      </ItemContent>
      <Badge variant="outline" className="border-foreground">
        Formato
      </Badge>
    </Item>
  );
}
