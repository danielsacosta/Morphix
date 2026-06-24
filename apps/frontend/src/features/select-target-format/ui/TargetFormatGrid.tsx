import { ConversionIcon, type ConversionPair } from '../../../entities/conversion';
import { cn } from '../../../shared/lib/utils';
import { Button } from '../../../shared/ui/button';

interface TargetFormatGridProps {
  options: ConversionPair[];
  targetFormat: string;
  onSelect: (targetFormat: string) => void;
}

export function TargetFormatGrid({ options, targetFormat, onSelect }: TargetFormatGridProps) {
  if (options.length === 0) return null;

  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3" aria-label="Target formats">
      {options.map((option) => (
        <Button
          key={`${option.source}-${option.target}`}
          variant="outline"
          className={cn(
            'h-auto min-h-28 flex-col items-start justify-center gap-2 whitespace-normal border-border/70 bg-background/35 p-4 text-left hover:border-primary/70 hover:bg-primary/10',
            targetFormat === option.target && 'border-primary/80 bg-primary/15 text-foreground ring-1 ring-primary/35',
          )}
          type="button"
          aria-pressed={targetFormat === option.target}
          onClick={() => onSelect(option.target)}
        >
          <ConversionIcon category={option.category} className="size-5 text-primary" />
          <span className="text-base font-semibold">{option.target.toUpperCase()}</span>
          <span className="text-xs text-muted-foreground">{option.engine}</span>
        </Button>
      ))}
    </div>
  );
}
