import { Activity, AlertTriangle, BriefcaseBusiness, Clock3, Play, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { SourceStatusPanel } from "./SourceStatusPanel";
type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
  running: boolean;
  refreshing: boolean;
  onRunNow: () => void;
  onRefresh: () => void;
};
export function IngestionOperationsPanel({
  employers,
  sources,
  runs,
  running,
  refreshing,
  onRunNow,
  onRefresh,
}: Props) {
  const allRuns = Object.values(runs)
    .flat()
    .sort((a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime());
  const failedRuns = allRuns.filter(
    (run) => !run.complete || !["success", "empty"].includes(run.outcome),
  ).length;
  const newJobs = allRuns.reduce((total, run) => total + run.jobs_inserted, 0);
  const metrics = [
    { label: "Registered employers", value: employers.length, icon: BriefcaseBusiness },
    { label: "Registered sources", value: sources.length, icon: Activity },
    { label: "Recorded retrievals", value: allRuns.length, icon: Clock3 },
    { label: "New vacancies from runs", value: newJobs, icon: BriefcaseBusiness },
  ];
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto py-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-semibold">Ingestion operations</h2>
          <p className="text-sm text-muted-foreground">
            Monitor source retrievals and inspect recent extraction activity.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onRefresh} disabled={refreshing || running}>
            <RefreshCw className={refreshing ? "mr-2 h-4 w-4 animate-spin" : "mr-2 h-4 w-4"} />{" "}
            Refresh
          </Button>
          <Button onClick={onRunNow} disabled={running || !sources.length}>
            <Play className="mr-2 h-4 w-4" /> {running ? "Retrieval running…" : "Run retrieval now"}
          </Button>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-sm">{label}</span>
              <Icon className="h-4 w-4" />
            </div>
            <p className="mt-2 text-2xl font-semibold tabular-nums">{value}</p>
          </div>
        ))}
      </div>
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
        <section className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold">Automatic retrieval</h3>
            <Badge variant="secondary">Not active</Badge>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">Target cadence: every 12 hours.</p>
          <p className="mt-2 text-sm text-muted-foreground">
            The automatic scheduler is not connected to the backend yet. A countdown will appear
            only when a real next-run time is available.
          </p>
        </section>
        <section className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold">Retrieval health</h3>
            <Badge variant={failedRuns ? "destructive" : "secondary"}>
              {failedRuns} unsuccessful runs
            </Badge>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">
            Totals reflect persisted extraction history, not accepted requests.
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            {allRuns.length
              ? `Most recent attempt: ${allRuns[0].started_at ? new Date(allRuns[0].started_at).toLocaleString() : "Unknown"}`
              : "No extraction runs have been recorded."}
          </p>
          {failedRuns > 0 && (
            <p className="mt-2 flex items-center gap-2 text-sm text-destructive">
              <AlertTriangle className="h-4 w-4" /> Review failed or partial runs below.
            </p>
          )}
        </section>
      </div>
      <SourceStatusPanel employers={employers} sources={sources} runs={runs} />
    </section>
  );
}
