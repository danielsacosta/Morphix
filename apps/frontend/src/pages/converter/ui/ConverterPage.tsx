import { useEffect, useMemo, useState } from 'react';
import { Activity, BarChart3, Clock3, FilePlus2 } from 'lucide-react';
import { ActiveJobsWidget } from '../../../widgets/active-jobs';
import { AppFooter, AppHeader, type AppSection } from '../../../widgets/app-shell';
import { ConversionOverviewWidget } from '../../../widgets/conversion-overview';
import { ConversionWorkspace } from '../../../widgets/conversion-workspace';
import { JobsHistoryWidget } from '../../../widgets/jobs-history';

const sections: Array<{ id: AppSection; label: string; detail: string; icon: typeof FilePlus2 }> = [
  { id: 'convertir', label: 'Convertir', detail: 'Nueva operación', icon: FilePlus2 },
  { id: 'activos', label: 'En proceso', detail: 'Cola en vivo', icon: Activity },
  { id: 'historial', label: 'Historial', detail: 'Archivos recientes', icon: Clock3 },
  { id: 'resumen', label: 'Resumen', detail: 'Métricas de sesión', icon: BarChart3 },
];

const viewCopy: Record<AppSection, { kicker: string; title: string; description: string }> = {
  convertir: {
    kicker: 'Convertir',
    title: 'Convierte tus archivos.',
    description: 'Carga, elige el formato y confirma el resultado en un flujo claro.',
  },
  activos: {
    kicker: '02 / cola en vivo',
    title: 'Mira cada trabajo avanzar.',
    description: 'Estado, progreso y acciones importantes en una sola lista operativa.',
  },
  historial: {
    kicker: '03 / archivo de sesión',
    title: 'Todo lo que ya procesaste.',
    description: 'Descarga resultados o elimina trabajos anteriores sin buscar entre paneles.',
  },
  resumen: {
    kicker: '04 / lectura rápida',
    title: 'Entiende tu actividad.',
    description: 'Una vista compacta de volumen, rendimiento y formatos más usados.',
  },
};

function getSectionFromHash(): AppSection {
  if (typeof window === 'undefined') return 'convertir';
  const hash = window.location.hash.replace('#', '') as AppSection;
  return sections.some((section) => section.id === hash) ? hash : 'convertir';
}

export function ConverterPage() {
  const [activeSection, setActiveSection] = useState<AppSection>(getSectionFromHash);
  const copy = useMemo(() => viewCopy[activeSection], [activeSection]);

  useEffect(() => {
    const onHashChange = () => setActiveSection(getSectionFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  function navigate(section: AppSection) {
    setActiveSection(section);
    window.history.replaceState(null, '', `#${section}`);
  }

  return (
    <div id="top" className="min-h-screen">
      <AppHeader activeSection={activeSection} onNavigate={navigate} />

      <div className="mx-auto grid w-full max-w-none lg:grid-cols-[236px_minmax(0,1fr)]">
        <aside className="hidden border-r-2 border-border lg:block" aria-label="Navegación del espacio de trabajo">
          <div className="sticky top-[82px] grid gap-8 p-6">
            <div className="grid gap-2 border-b-2 border-border pb-6">
              <span className="font-mono text-[0.65rem] font-black tracking-[0.18em] text-muted-foreground uppercase">Morphix / workspace</span>
              <p className="text-2xl font-black leading-[0.95] tracking-[-0.06em]">Operaciones de archivo.</p>
            </div>

            <nav className="grid gap-2" aria-label="Secciones principales">
              {sections.map((section, index) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;

                return (
                  <a
                    key={section.id}
                    href={`#${section.id}`}
                    onClick={() => navigate(section.id)}
                    aria-current={isActive ? 'page' : undefined}
                    className={`group grid grid-cols-[auto_1fr_auto] items-center gap-3 border-2 px-3 py-3 transition-colors ${
                      isActive ? 'border-foreground bg-foreground text-background shadow-[4px_4px_0_var(--shadow)] dark:border-primary dark:bg-primary dark:text-primary-foreground' : 'border-transparent hover:border-border hover:bg-accent'
                    }`}
                  >
                    <Icon className="size-4" aria-hidden="true" />
                    <span className="grid gap-0.5">
                      <span className="font-bold">{section.label}</span>
                      <span className={`font-mono text-[0.6rem] tracking-[0.1em] uppercase ${isActive ? 'text-background/60' : 'text-muted-foreground'}`}>{section.detail}</span>
                    </span>
                    <span className={`font-mono text-[0.65rem] font-bold ${isActive ? 'text-accent' : 'text-muted-foreground'}`}>{String(index + 1).padStart(2, '0')}</span>
                  </a>
                );
              })}
            </nav>

          </div>
        </aside>

        <main className="min-w-0 overflow-x-hidden px-4 py-7 sm:px-6 lg:px-10 lg:py-10">
          <div className="mx-auto grid w-full max-w-none gap-8">
            <header className="grid gap-5 border-b-2 border-border pb-7">
              <div className="grid min-w-0 gap-3">
                <span className="font-mono text-[0.68rem] font-black tracking-[0.18em] text-primary uppercase">{copy.kicker}</span>
                <h1 className="max-w-3xl text-4xl font-black leading-[0.94] tracking-[-0.07em] sm:text-6xl">{copy.title}</h1>
                <p className="max-w-2xl text-base font-medium leading-relaxed text-muted-foreground sm:text-lg">{copy.description}</p>
              </div>
            </header>

            <div className={activeSection === 'convertir' ? 'block' : 'hidden'}>
              <ConversionWorkspace />
            </div>
            <div className={activeSection === 'activos' ? 'block' : 'hidden'}>
              <ActiveJobsWidget />
            </div>
            <div className={activeSection === 'historial' ? 'block' : 'hidden'}>
              <JobsHistoryWidget />
            </div>
            <div className={activeSection === 'resumen' ? 'block' : 'hidden'}>
              <ConversionOverviewWidget />
            </div>
          </div>
        </main>
      </div>

      <AppFooter />
    </div>
  );
}
