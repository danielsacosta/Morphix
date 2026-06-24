import { FileAudio, FileImage, FileText } from 'lucide-react';
import { cn } from '../../../shared/lib/utils';
import type { ConversionPair } from '../model/conversionTypes';

interface ConversionIconProps {
  category?: ConversionPair['category'];
  className?: string;
}

export function ConversionIcon({ category, className }: ConversionIconProps) {
  const iconClassName = cn('size-4', className);

  if (category === 'images') return <FileImage className={iconClassName} aria-hidden="true" />;
  if (category === 'media') return <FileAudio className={iconClassName} aria-hidden="true" />;
  return <FileText className={iconClassName} aria-hidden="true" />;
}
