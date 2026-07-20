import type { ConversionPair } from './conversionTypes';

export const SUPPORTED_CONVERSIONS: ConversionPair[] = [
  { source: 'docx', target: 'pdf', label: 'Word a PDF', description: 'Documento listo para compartir', category: 'documents' },
  { source: 'xlsx', target: 'pdf', label: 'Excel a PDF', description: 'Hoja de cálculo con presentación final', category: 'documents' },
  { source: 'pptx', target: 'pdf', label: 'PowerPoint a PDF', description: 'Presentación estable para enviar', category: 'documents' },
  { source: 'pdf', target: 'docx', label: 'PDF a Word', description: 'Archivo editable para continuar trabajando', category: 'documents' },
  { source: 'pdf', target: 'txt', label: 'PDF a TXT', description: 'Texto plano para reutilizar el contenido', category: 'documents' },
  { source: 'pdf', target: 'html', label: 'PDF a HTML', description: 'Contenido listo para publicar en web', category: 'documents' },
  { source: 'pdf', target: 'png', label: 'PDF a PNG', description: 'Primera página como imagen nítida', category: 'images' },
  { source: 'pdf', target: 'jpg', label: 'PDF a JPG', description: 'Primera página como imagen compatible', category: 'images' },
  { source: 'docx', target: 'txt', label: 'Word a TXT', description: 'Texto plano para trabajar sin formato', category: 'documents' },
  { source: 'docx', target: 'odt', label: 'Word a ODT', description: 'Documento abierto y editable', category: 'documents' },
  { source: 'docx', target: 'html', label: 'Word a HTML', description: 'Documento listo para web', category: 'documents' },
  { source: 'xlsx', target: 'ods', label: 'Excel a ODS', description: 'Hoja de cálculo en formato abierto', category: 'documents' },
  { source: 'pptx', target: 'odp', label: 'PowerPoint a ODP', description: 'Presentación en formato abierto', category: 'documents' },
  { source: 'pptx', target: 'txt', label: 'PowerPoint a TXT', description: 'Texto de la presentación para reutilizar', category: 'documents' },
  { source: 'csv', target: 'xlsx', label: 'CSV a Excel', description: 'Datos organizados en formato de hoja', category: 'documents' },
  { source: 'xlsx', target: 'csv', label: 'Excel a CSV', description: 'Datos limpios para importar o analizar', category: 'documents' },
  { source: 'csv', target: 'pdf', label: 'CSV a PDF', description: 'Datos listos para compartir', category: 'documents' },
  { source: 'csv', target: 'ods', label: 'CSV a ODS', description: 'Datos en una hoja abierta y editable', category: 'documents' },
  { source: 'png', target: 'jpg', label: 'PNG a JPG', description: 'Imagen liviana y compatible', category: 'images' },
  { source: 'jpg', target: 'png', label: 'JPG a PNG', description: 'Imagen preparada para edición', category: 'images' },
  { source: 'jpg', target: 'webp', label: 'JPG a WebP', description: 'Imagen optimizada para web', category: 'images' },
  { source: 'png', target: 'webp', label: 'PNG a WebP', description: 'Imagen moderna y eficiente', category: 'images' },
  { source: 'png', target: 'gif', label: 'PNG a GIF', description: 'Imagen compatible con gráficos simples', category: 'images' },
  { source: 'png', target: 'tiff', label: 'PNG a TIFF', description: 'Imagen para flujos de alta calidad', category: 'images' },
  { source: 'png', target: 'bmp', label: 'PNG a BMP', description: 'Imagen sin compresión para compatibilidad', category: 'images' },
  { source: 'jpg', target: 'gif', label: 'JPG a GIF', description: 'Imagen en formato gráfico clásico', category: 'images' },
  { source: 'jpg', target: 'tiff', label: 'JPG a TIFF', description: 'Imagen para edición y archivo', category: 'images' },
  { source: 'jpg', target: 'bmp', label: 'JPG a BMP', description: 'Imagen sin compresión para compatibilidad', category: 'images' },
  { source: 'svg', target: 'png', label: 'SVG a PNG', description: 'Gráfico vectorial listo para usar', category: 'images' },
  { source: 'svg', target: 'jpg', label: 'SVG a JPG', description: 'Gráfico vectorial en imagen compatible', category: 'images' },
  { source: 'gif', target: 'png', label: 'GIF a PNG', description: 'Imagen preparada para edición', category: 'images' },
  { source: 'tiff', target: 'jpg', label: 'TIFF a JPG', description: 'Imagen optimizada para compartir', category: 'images' },
  { source: 'mp4', target: 'mp3', label: 'MP4 a MP3', description: 'Audio extraído del video', category: 'media' },
  { source: 'mp4', target: 'webm', label: 'MP4 a WebM', description: 'Video preparado para web', category: 'media' },
  { source: 'mov', target: 'mp4', label: 'MOV a MP4', description: 'Video compatible con más plataformas', category: 'media' },
  { source: 'avi', target: 'mp4', label: 'AVI a MP4', description: 'Video compatible con más plataformas', category: 'media' },
  { source: 'avi', target: 'webm', label: 'AVI a WebM', description: 'Video preparado para web', category: 'media' },
  { source: 'mkv', target: 'mp4', label: 'MKV a MP4', description: 'Video compatible para compartir', category: 'media' },
  { source: 'mkv', target: 'webm', label: 'MKV a WebM', description: 'Video preparado para web', category: 'media' },
  { source: 'mov', target: 'webm', label: 'MOV a WebM', description: 'Video preparado para web', category: 'media' },
  { source: 'm4v', target: 'mp4', label: 'M4V a MP4', description: 'Video compatible con más plataformas', category: 'media' },
  { source: 'flv', target: 'mp4', label: 'FLV a MP4', description: 'Video compatible para compartir', category: 'media' },
  { source: '3gp', target: 'mp4', label: '3GP a MP4', description: 'Video móvil compatible', category: 'media' },
  { source: 'wav', target: 'mp3', label: 'WAV a MP3', description: 'Audio comprimido para compartir', category: 'media' },
  { source: 'mp3', target: 'wav', label: 'MP3 a WAV', description: 'Audio en formato de trabajo', category: 'media' },
  { source: 'aac', target: 'mp3', label: 'AAC a MP3', description: 'Audio comprimido y compatible', category: 'media' },
  { source: 'flac', target: 'mp3', label: 'FLAC a MP3', description: 'Audio optimizado para compartir', category: 'media' },
  { source: 'ogg', target: 'mp3', label: 'OGG a MP3', description: 'Audio compatible con más dispositivos', category: 'media' },
  { source: 'm4a', target: 'mp3', label: 'M4A a MP3', description: 'Audio listo para compartir', category: 'media' },
  { source: 'opus', target: 'wav', label: 'OPUS a WAV', description: 'Audio en formato de trabajo', category: 'media' },
  { source: 'aiff', target: 'mp3', label: 'AIFF a MP3', description: 'Audio comprimido para compartir', category: 'media' },
  { source: 'aiff', target: 'wav', label: 'AIFF a WAV', description: 'Audio en formato de trabajo', category: 'media' },
];

export function targetsForSource(source: string): ConversionPair[] {
  return SUPPORTED_CONVERSIONS.filter((conversion) => conversion.source === source);
}

export function acceptedExtensions(): string {
  return Array.from(new Set(SUPPORTED_CONVERSIONS.map((conversion) => `.${conversion.source}`))).join(',');
}

export function findConversionPair(source?: string, target?: string): ConversionPair | undefined {
  return SUPPORTED_CONVERSIONS.find((conversion) => conversion.source === source && conversion.target === target);
}
