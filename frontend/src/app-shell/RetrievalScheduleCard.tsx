import { AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { ExtractionRun } from "../api";

type Props = { runs: ExtractionRun[] };

export function RetrievalScheduleCard({ runs }: Props) {
  const failed = runs.filter((run) => !run.complete || !["success", "empty"].includes(run.outcome)).length;
  const latest = [...runs].sort((a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime())[0];
  return <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
    <section className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between gap-2"><h3 className="font-semibold">Automatic retrieval</h3><Badge variant="secondary">Not active</Badge></div>
      <p className="mt-3 text-sm text-muted-foreground">Target cadence: every 12 hours.</p>
      <p className="mt-2 text-sm text-muted-foreground">The automatic scheduler is not connected to the backend yet. A countdown will appear only when a real next-run time is available.</p>
    </section>
    <section className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between gap-2"><h3 className="font-semibold">Retrieval health</h3><Badge variant={failed ? "destructive" : "secondary"}>{failed} unsuccessful runs</Badge></div>
      <p className="mt-3 text-sm text-muted-foreground">Totals reflect persisted extraction history, not accepted requests.</p>
      <p className="mt-2 text-sm text-muted-foreground">{latest?.started_at ? `Most recent attempt: ${new Date(latest.started_at).toLocaleString()}` : "No extraction runs have been recorded."}</p>
      {failed > 0 && <p className="mt-2 flex items-center gap-2 text-sm text-destructive"><AlertTriangle className="h-4 w-4" /> Review failed or partial runs below.</p>}
    </section>
  </div>;
}
