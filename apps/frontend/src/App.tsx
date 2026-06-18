import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowDownToLine,
  CheckCircle2,
  Clock3,
  FileArchive,
  FileAudio,
  FileImage,
  FileText,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Trash2,
  UploadCloud,
  XCircle,
} from 'lucide-react';
import {
  createJob,
  deleteJob,
  getDownloadUrl,
  getJob,
  getUploadUrl,
  listJobs,
  startJob,
  uploadFile,
} from './api';
import { acceptedExtensions, normalizeExtension, SUPPORTED_CONVERSIONS, targetsForSource } from './conversions';
import { config } from './config';
import type { ConversionPair, JobRecord, JobStatus } from './types';

type FlowState = 'idle' | 'creating' | 'uploading' | 'starting' | 'polling' | 'ready' | 'failed';

const statusLabel: Record<JobStatus, string> = {
  PENDING: 'Pendiente',
  UPLOAD_REQUESTED: 'Subida autorizada',
  UPLOADED: 'Archivo cargado',
  PROCESSING: 'Procesando',
  COMPLETED: 'Completado',
  FAILED: 'Fallido',
  EXPIRED: 'Expirado',
  DELETED: 'Eliminado',
};

const statusTone: Record<JobStatus, string> = {
  PENDING: 'neutral',
  UPLOAD_REQUESTED: 'accent',
  UPLOADED: 'accent',
  PROCESSING: 'warn',
  COMPLETED: 'success',
  FAILED: 'danger',
  EXPIRED: 'danger',
  DELETED: 'neutral',
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function iconFor(category?: ConversionPair['category']) {
  if (category === 'images') return <FileImage aria-hidden="true" />;
  if (category === 'media') return <FileAudio aria-hidden="true" />;
  return <FileText aria-hidden="true" />;
}

function findPair(source?: string, target?: string) {
  return SUPPORTED_CONVERSIONS.find((conversion) => conversion.source === source && conversion.target === target);
}

function App() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [targetFormat, setTargetFormat] = useState('');
  const [currentJob, setCurrentJob] = useState<JobRecord | null>(null);
  const [jobs, setJobs] = useState<JobRecord[]>([]);
  const [flowState, setFlowState] = useState<FlowState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setRefreshing] = useState(false);

  const sourceFormat = file ? normalizeExtension(file.name) : '';
  const targetOptions = useMemo(() => targetsForSource(sourceFormat), [sourceFormat]);
  const selectedPair = findPair(sourceFormat, targetFormat);
  const fileTooLarge = Boolean(file && file.size > config.maxFileSizeBytes);
  const canStart = Boolean(file && targetFormat && !fileTooLarge && flowState !== 'creating' && flowState !== 'uploading' && flowState !== 'starting' && flowState !== 'polling');

  async function refreshJobs() {
    setRefreshing(true);
    try {
      const nextJobs = await listJobs();
      setJobs(nextJobs);
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : 'No se pudo consultar el historial.');
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void refreshJobs();
  }, []);

  useEffect(() => {
    if (!sourceFormat) {
      setTargetFormat('');
      return;
    }

    const firstTarget = targetsForSource(sourceFormat)[0]?.target || '';
    setTargetFormat(firstTarget);
  }, [sourceFormat]);

  useEffect(() => {
    if (!currentJob || !['PENDING', 'UPLOAD_REQUESTED', 'UPLOADED', 'PROCESSING'].includes(currentJob.status)) {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const latest = await getJob(currentJob.job_id);
        setCurrentJob(latest);
        setJobs((previous) => [latest, ...previous.filter((job) => job.job_id !== latest.job_id)]);

        if (latest.status === 'COMPLETED') {
          setFlowState('ready');
          window.clearInterval(timer);
        }

        if (latest.status === 'FAILED') {
          setFlowState('failed');
          setError(latest.error_message || 'No fue posible convertir el archivo.');
          window.clearInterval(timer);
        }
      } catch (pollError) {
        setFlowState('failed');
        setError(pollError instanceof Error ? pollError.message : 'No se pudo consultar el estado.');
        window.clearInterval(timer);
      }
    }, 2500);

    return () => window.clearInterval(timer);
  }, [currentJob]);

  async function handleConvert() {
    if (!file || !targetFormat) return;

    setError(null);
    setFlowState('creating');

    try {
      const created = await createJob(file, targetFormat);
      setCurrentJob(created.job);

      setFlowState('uploading');
      const upload = await getUploadUrl(created.job.job_id, file.type);
      await uploadFile(upload, file);

      setFlowState('starting');
      const started = await startJob(created.job.job_id);
      setCurrentJob(started);
      setJobs((previous) => [started, ...previous.filter((job) => job.job_id !== started.job_id)]);
      setFlowState('polling');
    } catch (conversionError) {
      setFlowState('failed');
      setError(conversionError instanceof Error ? conversionError.message : 'La conversion no pudo iniciarse.');
    }
  }

  async function handleDownload(job: JobRecord) {
    setError(null);
    try {
      const download = await getDownloadUrl(job.job_id);
      window.location.href = download.download_url;
    } catch (downloadError) {
      setError(downloadError instanceof Error ? downloadError.message : 'No se pudo crear la URL de descarga.');
    }
  }

  async function handleDelete(job: JobRecord) {
    setError(null);
    try {
      await deleteJob(job.job_id);
      setJobs((previous) => previous.filter((item) => item.job_id !== job.job_id));
      if (currentJob?.job_id === job.job_id) {
        setCurrentJob(null);
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'No se pudo eliminar el job.');
    }
  }

  function selectFile(nextFile: File | null) {
    setFile(nextFile);
    setCurrentJob(null);
    setFlowState('idle');
    setError(null);
  }

  const progressSteps = [
    { key: 'creating', label: 'Job', active: Boolean(currentJob), done: Boolean(currentJob) },
    { key: 'uploading', label: 'Upload', active: flowState === 'uploading', done: ['starting', 'polling', 'ready'].includes(flowState) },
    { key: 'polling', label: 'Worker', active: flowState === 'polling', done: flowState === 'ready' },
    { key: 'ready', label: 'Download', active: flowState === 'ready', done: flowState === 'ready' },
  ];

  return (
    <main className="app-shell">
      <section className="workspace">
        <aside className="side-panel" aria-label="Morphix overview">
          <div className="brand-block">
            <div className="brand-mark">
              <FileArchive aria-hidden="true" />
            </div>
            <div>
              <p className="eyebrow">Morphix</p>
              <h1>Conversion asincrona de archivos</h1>
            </div>
          </div>

          <div className="metric-grid" aria-label="Supported conversion coverage">
            <div>
              <strong>15</strong>
              <span>pares MVP</span>
            </div>
            <div>
              <strong>100 MB</strong>
              <span>limite inicial</span>
            </div>
            <div>
              <strong>S3</strong>
              <span>upload directo</span>
            </div>
            <div>
              <strong>ECS</strong>
              <span>worker aislado</span>
            </div>
          </div>

          <div className="engine-list" aria-label="Conversion engines">
            <div><ShieldCheck aria-hidden="true" /> LibreOffice</div>
            <div><ShieldCheck aria-hidden="true" /> FFmpeg</div>
            <div><ShieldCheck aria-hidden="true" /> ImageMagick</div>
            <div><ShieldCheck aria-hidden="true" /> PyMuPDF</div>
          </div>
        </aside>

        <section className="converter-panel" aria-label="File converter">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Nuevo job</p>
              <h2>Convierte un archivo</h2>
            </div>
            <button className="icon-button" type="button" onClick={() => inputRef.current?.click()} aria-label="Seleccionar archivo">
              <UploadCloud aria-hidden="true" />
            </button>
          </div>

          <label
            className={`drop-zone ${file ? 'has-file' : ''}`}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              selectFile(event.dataTransfer.files.item(0));
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept={acceptedExtensions()}
              onChange={(event) => selectFile(event.currentTarget.files?.item(0) ?? null)}
            />
            <UploadCloud aria-hidden="true" />
            <span>{file ? file.name : 'Arrastra o selecciona un archivo'}</span>
            <small>{file ? `${formatBytes(file.size)} · ${sourceFormat.toUpperCase()}` : acceptedExtensions().replaceAll('.', '').toUpperCase()}</small>
          </label>

          {fileTooLarge && <p className="error-text">El archivo supera el limite configurado de {config.maxFileSizeMb} MB.</p>}
          {file && targetOptions.length === 0 && <p className="error-text">El formato {sourceFormat.toUpperCase()} no esta soportado por el MVP.</p>}

          <div className="format-grid" aria-label="Target formats">
            {targetOptions.map((option) => (
              <button
                key={`${option.source}-${option.target}`}
                className={`format-option ${targetFormat === option.target ? 'selected' : ''}`}
                type="button"
                onClick={() => setTargetFormat(option.target)}
              >
                {iconFor(option.category)}
                <span>{option.target.toUpperCase()}</span>
                <small>{option.engine}</small>
              </button>
            ))}
          </div>

          <button className="primary-action" type="button" disabled={!canStart} onClick={handleConvert}>
            {['creating', 'uploading', 'starting', 'polling'].includes(flowState) ? <Loader2 className="spin" aria-hidden="true" /> : <RefreshCw aria-hidden="true" />}
            <span>{flowState === 'polling' ? 'Procesando' : 'Iniciar conversion'}</span>
          </button>

          <div className="progress-strip" aria-label="Conversion progress">
            {progressSteps.map((step) => (
              <div key={step.key} className={`progress-step ${step.active ? 'active' : ''} ${step.done ? 'done' : ''}`}>
                <span />
                <small>{step.label}</small>
              </div>
            ))}
          </div>

          {selectedPair && (
            <div className="selected-route">
              {iconFor(selectedPair.category)}
              <div>
                <strong>{selectedPair.label}</strong>
                <span>{selectedPair.engine} en worker ECS Fargate</span>
              </div>
            </div>
          )}

          {currentJob && (
            <div className="current-job">
              <div>
                <span className={`status-pill ${statusTone[currentJob.status]}`}>{statusLabel[currentJob.status]}</span>
                <strong>{currentJob.source_format.toUpperCase()} a {currentJob.target_format.toUpperCase()}</strong>
                <small>{currentJob.job_id}</small>
              </div>
              {currentJob.status === 'COMPLETED' && (
                <button className="secondary-action" type="button" onClick={() => handleDownload(currentJob)}>
                  <ArrowDownToLine aria-hidden="true" />
                  Descargar
                </button>
              )}
            </div>
          )}

          {error && (
            <div className="error-banner" role="alert">
              <XCircle aria-hidden="true" />
              <span>{error}</span>
            </div>
          )}
        </section>
      </section>

      <section className="history-section" aria-label="Conversion history">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Historial</p>
            <h2>Conversiones recientes</h2>
          </div>
          <button className="secondary-action" type="button" onClick={refreshJobs} disabled={isRefreshing}>
            {isRefreshing ? <Loader2 className="spin" aria-hidden="true" /> : <RefreshCw aria-hidden="true" />}
            Actualizar
          </button>
        </div>

        <div className="history-list">
          {jobs.length === 0 && (
            <div className="empty-state">
              <Clock3 aria-hidden="true" />
              <span>Sin conversiones registradas para este usuario.</span>
            </div>
          )}

          {jobs.map((job) => {
            const pair = findPair(job.source_format, job.target_format);
            return (
              <article className="history-row" key={job.job_id}>
                <div className="history-icon">{iconFor(pair?.category)}</div>
                <div className="history-main">
                  <strong>{job.source_format.toUpperCase()} a {job.target_format.toUpperCase()}</strong>
                  <span>{new Date(job.created_at).toLocaleString()} · {formatBytes(job.file_size)}</span>
                </div>
                <span className={`status-pill ${statusTone[job.status]}`}>
                  {job.status === 'COMPLETED' && <CheckCircle2 aria-hidden="true" />}
                  {job.status === 'FAILED' && <XCircle aria-hidden="true" />}
                  {statusLabel[job.status]}
                </span>
                <div className="row-actions">
                  <button className="icon-button" type="button" onClick={() => handleDownload(job)} disabled={job.status !== 'COMPLETED'} aria-label="Descargar resultado">
                    <ArrowDownToLine aria-hidden="true" />
                  </button>
                  <button className="icon-button danger" type="button" onClick={() => handleDelete(job)} aria-label="Eliminar job">
                    <Trash2 aria-hidden="true" />
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}

export default App;

