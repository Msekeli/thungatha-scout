import { Activity, BriefcaseBusiness, Clock3, Play, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { SourceStatusPanel } from "./SourceStatusPanel";
import { RetrievalScheduleCard } from "./RetrievalScheduleCard";
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
  const newJobs = allRuns.reduce((total, run) => total + run.jobs_inserted, 0);
  const metrics = [
    { label: "Registered employers", value: employers.length, icon: BriefcaseBusiness },
    { label: "Registered sources", value: sources.length, icon: Activity },
    { label: "Recent retrieval runs", value: allRuns.length, icon: Clock3 },
    { label: "New vacancies in history", value: newJobs, icon: BriefcaseBusiness },
  ];
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 py-4">
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-3">
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
      <div className="grid shrink-0 gap-3 sm:grid-cols-2 xl:grid-cols-4">
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
      <div className="shrink-0">
        <RetrievalScheduleCard runs={allRuns} />
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto">
        <SourceStatusPanel employers={employers} sources={sources} runs={runs} />
      </div>
    </section>
  );
}
