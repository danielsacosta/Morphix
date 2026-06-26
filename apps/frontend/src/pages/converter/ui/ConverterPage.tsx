import { useState } from 'react';
import { ConversionWorkspace } from '../../../widgets/conversion-workspace';
import { AppFooter, AppHeader } from '../../../widgets/app-shell';
import { ConversionOverviewWidget } from '../../../widgets/conversion-overview';
import { JobsHistoryWidget } from '../../../widgets/jobs-history';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../shared/ui/tabs';

type PanelView = 'history' | 'overview';

export function ConverterPage() {
  const [activeView, setActiveView] = useState<PanelView>('history');

  return (
    <div id="top" className="min-h-screen">
      <AppHeader activeView={activeView} onViewChange={setActiveView} />
      <main className="mx-auto grid w-full max-w-7xl gap-5 px-4 py-5 sm:px-6 lg:py-8">
        <div className="grid gap-5 lg:grid-cols-[1.4fr_1fr]">
          <div className="w-full">
            <ConversionWorkspace />
          </div>

          <div id="panel" className="scroll-mt-24">
            <Tabs value={activeView} onValueChange={(value) => setActiveView(value as PanelView)} className="h-full">
              <TabsList className="w-full">
                <TabsTrigger value="history">Historial</TabsTrigger>
                <TabsTrigger value="overview">Resumen</TabsTrigger>
              </TabsList>
              <TabsContent value="history" className="min-h-0">
                <JobsHistoryWidget />
              </TabsContent>
              <TabsContent value="overview" className="min-h-0">
                <ConversionOverviewWidget />
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>
      <AppFooter />
    </div>
  );
}
