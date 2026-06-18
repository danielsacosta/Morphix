import type { ConversionPair } from './types';

export const SUPPORTED_CONVERSIONS: ConversionPair[] = [
  { source: 'docx', target: 'pdf', label: 'Word a PDF', engine: 'LibreOffice', category: 'documents' },
  { source: 'xlsx', target: 'pdf', label: 'Excel a PDF', engine: 'LibreOffice', category: 'documents' },
  { source: 'pptx', target: 'pdf', label: 'PowerPoint a PDF', engine: 'LibreOffice', category: 'documents' },
  { source: 'pdf', target: 'docx', label: 'PDF a Word', engine: 'PyMuPDF / pdf2docx', category: 'documents' },
  { source: 'csv', target: 'xlsx', label: 'CSV a Excel', engine: 'openpyxl', category: 'documents' },
  { source: 'xlsx', target: 'csv', label: 'Excel a CSV', engine: 'openpyxl', category: 'documents' },
  { source: 'png', target: 'jpg', label: 'PNG a JPG', engine: 'ImageMagick', category: 'images' },
  { source: 'jpg', target: 'png', label: 'JPG a PNG', engine: 'ImageMagick', category: 'images' },
  { source: 'jpg', target: 'webp', label: 'JPG a WebP', engine: 'ImageMagick', category: 'images' },
  { source: 'png', target: 'webp', label: 'PNG a WebP', engine: 'ImageMagick', category: 'images' },
  { source: 'mp4', target: 'mp3', label: 'MP4 a MP3', engine: 'FFmpeg', category: 'media' },
  { source: 'mp4', target: 'webm', label: 'MP4 a WebM', engine: 'FFmpeg', category: 'media' },
  { source: 'mov', target: 'mp4', label: 'MOV a MP4', engine: 'FFmpeg', category: 'media' },
  { source: 'wav', target: 'mp3', label: 'WAV a MP3', engine: 'FFmpeg', category: 'media' },
  { source: 'mp3', target: 'wav', label: 'MP3 a WAV', engine: 'FFmpeg', category: 'media' },
];

export function normalizeExtension(name: string): string {
  const last = name.split('.').pop();
  return last?.toLowerCase() === 'jpeg' ? 'jpg' : last?.toLowerCase() || '';
}

export function targetsForSource(source: string): ConversionPair[] {
  return SUPPORTED_CONVERSIONS.filter((conversion) => conversion.source === source);
}

export function acceptedExtensions(): string {
  return Array.from(new Set(SUPPORTED_CONVERSIONS.map((conversion) => `.${conversion.source}`))).join(',');
}

