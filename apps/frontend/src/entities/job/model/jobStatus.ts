import type { JobStatus } from './jobTypes';

export const statusLabel: Record<JobStatus, string> = {
  PENDING: 'Preparando',
  UPLOAD_REQUESTED: 'Listo para cargar',
  UPLOADED: 'Archivo cargado',
  QUEUED: 'En cola',
  PROCESSING: 'Procesando',
  COMPLETED: 'Completado',
  FAILED: 'Fallido',
  EXPIRED: 'Expirado',
  DELETED: 'Eliminado',
};

export function isActiveJobStatus(status: JobStatus): boolean {
  return ['PENDING', 'UPLOAD_REQUESTED', 'UPLOADED', 'QUEUED', 'PROCESSING'].includes(status);
}
