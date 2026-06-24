import { ConversionOverview } from '../../../widgets/conversion-overview';
import { ConversionWorkspace } from '../../../widgets/conversion-workspace';
import { JobsHistoryWidget } from '../../../widgets/jobs-history';

export function ConverterPage() {
  return (
    <main className="mx-auto grid min-h-screen w-full max-w-6xl gap-5 px-4 py-5 sm:px-6 lg:py-8">
      <section className="grid items-stretch gap-5 lg:grid-cols-[minmax(280px,0.85fr)_minmax(360px,1.45fr)]">
        <ConversionOverview />
        <ConversionWorkspace />
      </section>
      <JobsHistoryWidget />
    </main>
  );
}
