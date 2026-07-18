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
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3" aria-label="Target formats">
      {options.map((option) => (
        <Button
          key={`${option.source}-${option.target}`}
          variant="outline"
          className={cn(
            'h-auto min-h-32 flex-col items-start justify-center gap-2 whitespace-normal border-border bg-card p-4 text-left hover:border-foreground hover:bg-accent',
            targetFormat === option.target && 'border-foreground bg-primary text-primary-foreground shadow-[4px_4px_0_var(--shadow)]',
          )}
          type="button"
          aria-pressed={targetFormat === option.target}
          onClick={() => onSelect(option.target)}
        >
          <ConversionIcon category={option.category} className={cn('size-5 group-hover/button:text-foreground', targetFormat === option.target ? 'text-primary-foreground' : 'text-primary')} />
          <span className="font-mono text-sm font-black tracking-[0.14em] group-hover/button:text-foreground">{option.target.toUpperCase()}</span>
          <span className={cn('text-xs leading-snug group-hover/button:text-foreground', targetFormat === option.target ? 'text-primary-foreground/80' : 'text-muted-foreground')}>{option.description}</span>
        </Button>
      ))}
    </div>
  );
}
