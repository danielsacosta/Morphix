import { useEffect, useState, type MouseEvent } from 'react';
import { flushSync } from 'react-dom';
import { ArrowUpRight, FileArchive, Moon, Sun } from 'lucide-react';
import { Button } from '../../../shared/ui/button';

export type AppSection = 'convertir' | 'activos' | 'historial' | 'resumen';

interface AppHeaderProps {
  activeSection: AppSection;
  onNavigate: (section: AppSection) => void;
}

const sectionLabels: Record<AppSection, string> = {
  convertir: 'Convertir',
  activos: 'En proceso',
  historial: 'Historial',
  resumen: 'Resumen',
};

export function AppHeader({ activeSection, onNavigate }: AppHeaderProps) {
  const [isDark, setIsDark] = useState(getInitialDarkMode);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    try {
      window.localStorage.setItem('morphix-theme', isDark ? 'dark' : 'light');
    } catch {
      // Keep the toggle functional when storage is unavailable.
    }
  }, [isDark]);

  function toggleTheme(event: MouseEvent<HTMLButtonElement>) {
    const nextThemeIsDark = !isDark;
    const root = document.documentElement;
    const rect = event.currentTarget.getBoundingClientRect();
    const originX = event.clientX || rect.left + rect.width / 2;
    const originY = event.clientY || rect.top + rect.height / 2;

    root.style.setProperty('--theme-origin-x', `${originX}px`);
    root.style.setProperty('--theme-origin-y', `${originY}px`);

    const startViewTransition = 'startViewTransition' in document ? document.startViewTransition.bind(document) : undefined;
    if (startViewTransition) {
      startViewTransition(() => {
        flushSync(() => setIsDark(nextThemeIsDark));
      });
      return;
    }

    setIsDark(nextThemeIsDark);
  }

  return (
    <header className="sticky top-0 z-30 border-b-2 border-border bg-background">
      <div className="mx-auto flex w-full max-w-none items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <a href="#convertir" onClick={() => onNavigate('convertir')} className="group flex min-w-0 items-center gap-3 outline-none focus-visible:ring-2 focus-visible:ring-ring">
          <span className="flex size-11 shrink-0 items-center justify-center border-2 border-foreground bg-primary text-primary-foreground shadow-[4px_4px_0_var(--shadow)] transition-transform group-hover:translate-x-0.5 group-hover:translate-y-0.5 group-hover:shadow-[2px_2px_0_var(--shadow)]">
            <FileArchive className="size-5" aria-hidden="true" />
          </span>
          <span className="grid min-w-0">
            <span className="truncate text-lg font-black leading-none tracking-[-0.04em] text-foreground">Morphix</span>
            <span className="truncate font-mono text-[0.62rem] font-bold tracking-[0.16em] text-muted-foreground uppercase">File operations</span>
          </span>
        </a>

        <Button
          variant="outline"
          size="icon"
          type="button"
          aria-label={isDark ? 'Activar modo claro' : 'Activar modo oscuro'}
          title={isDark ? 'Activar modo claro' : 'Activar modo oscuro'}
          aria-pressed={isDark}
          onClick={toggleTheme}
        >
          {isDark ? <Sun className="size-4" aria-hidden="true" /> : <Moon className="size-4" aria-hidden="true" />}
        </Button>

      </div>

      <nav className="mx-auto flex w-full max-w-none gap-1 overflow-x-auto border-t-2 border-border px-4 py-2 lg:hidden sm:px-6" aria-label="Secciones principales">
        {(Object.keys(sectionLabels) as AppSection[]).map((section) => (
          <a
            key={section}
            href={`#${section}`}
            onClick={() => onNavigate(section)}
            aria-current={activeSection === section ? 'page' : undefined}
            className={`whitespace-nowrap border-2 px-3 py-2 font-mono text-[0.68rem] font-black tracking-[0.12em] uppercase transition-colors ${
              activeSection === section ? 'border-foreground bg-foreground text-background dark:border-primary dark:bg-primary dark:text-primary-foreground' : 'border-transparent text-muted-foreground hover:border-border hover:text-foreground'
            }`}
          >
            {sectionLabels[section]}
            {section === 'convertir' && <ArrowUpRight className="ml-1 inline size-3" aria-hidden="true" />}
          </a>
        ))}
      </nav>
    </header>
  );
}

function getInitialDarkMode(): boolean {
  if (typeof window === 'undefined') return false;

  try {
    const storedTheme = window.localStorage.getItem('morphix-theme');
    if (storedTheme === 'dark' || storedTheme === 'light') return storedTheme === 'dark';
  } catch {
    // Fall back to the operating system preference.
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}
