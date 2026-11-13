import { Activity, AlertTriangle, BriefcaseBusiness, Clock3, Play, RefreshCw } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource, ExtractionRun } from "../api";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
  running: boolean;
  refreshing: boolean;
  onRunNow: () => void;
  onRefresh: () => void;
};

const dateLabel = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : "Not recorded";

export function IngestionOperationsPanel({
  employers, sources, runs, running, refreshing, onRunNow, onRefresh,
}: Props) {
  const allRuns = Object.values(runs).flat().sort(
    (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
  );
  const latestBySource = sources.map((source) => ({
    source,
    run: runs[source.id]?.[0],
    employer: employers.find((item) => item.id === source.employer_id),
  }));
  const failedRuns = allRuns.filter((run) => !["success", "empty"].includes(run.outcome)).length;
  const newJobs = allRuns.reduce((total, run) => total + run.jobs_inserted, 0);

  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto py-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-semibold">Ingestion operations</h2>
          <p className="text-sm text-muted-foreground">Monitor source retrievals and inspect recent extraction activity.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onRefresh} disabled={refreshing || running}>
            <RefreshCw className={refreshing ? "mr-2 h-4 w-4 animate-spin" : "mr-2 h-4 w-4"} /> Refresh
          </Button>
          <Button onClick={onRunNow} disabled={running || sources.length === 0}>
            <Play className="mr-2 h-4 w-4" /> {running ? "Retrieval running…" : "Run retrieval now"}
          </Button>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Registered employers", value: employers.length, icon: BriefcaseBusiness },
          { label: "Registered sources", value: sources.length, icon: Activity },
          { label: "Recorded retrievals", value: allRuns.length, icon: Clock3 },
          { label: "New vacancies from runs", value: newJobs, icon: BriefcaseBusiness },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="text-sm">{label}</span><Icon className="h-4 w-4" />
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
          <p className="mt-2 text-sm text-muted-foreground">The automatic scheduler is not connected to the backend yet. A countdown will appear only after a real schedule and next-run time are available.</p>
        </section>
        <section className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold">Retrieval health</h3>
            <Badge variant={failedRuns ? "destructive" : "secondary"}>{failedRuns} unsuccessful runs</Badge>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">Run totals reflect persisted extraction history. A run is not considered successful merely because its request was accepted.</p>
          <p className="mt-2 text-sm text-muted-foreground">{allRuns.length ? `Most recent attempt: ${dateLabel(allRuns[0].started_at)}` : "No extraction runs have been recorded."}</p>
          {failedRuns > 0 && <p className="mt-2 flex items-center gap-2 text-sm text-destructive"><AlertTriangle className="h-4 w-4" /> Review failed or partial runs below.</p>}
        </section>
      </div>

      <section className="overflow-hidden rounded-lg border bg-card">
        <div className="border-b px-4 py-3"><h3 className="font-semibold">Source status</h3></div>
        <div className="divide-y">
          {latestBySource.map(({ source, run, employer }) => (
            <div key={source.id} className="grid gap-2 px-4 py-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center">
              <div className="min-w-0">
                <p className="truncate font-medium">{employer?.name ?? "Unknown employer"}</p>
                <p className="truncate text-sm text-muted-foreground">{source.adapter_key} · {source.source_url}</p>
                <p className="text-xs text-muted-foreground">Last attempt: {dateLabel(run?.started_at)}</p>
              </div>
              <Badge variant={!run ? "outline" : run.complete && ["success", "empty"].includes(run.outcome) ? "secondary" : "destructive"}>
                {!run ? "Never retrieved" : run.outcome.replaceAll("_", " ")}
              </Badge>
            </div>
          ))}
          {!sources.length && <p className="px-4 py-6 text-sm text-muted-foreground">No registered sources yet.</p>}
        </div>
      </section>

      <section className="overflow-hidden rounded-lg border bg-card">
        <div className="border-b px-4 py-3"><h3 className="font-semibold">Recent retrievals</h3></div>
        <div className="divide-y">
          {allRuns.slice(0, 10).map((run) => {
            const source = sources.find((item) => item.id === run.source_id);
            const employer = employers.find((item) => item.id === source?.employer_id);
            return <div key={run.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
              <div><p className="font-medium">{employer?.name ?? "Unknown employer"} · {source?.adapter_key ?? "Unknown source"}</p>
                <p className="text-xs text-muted-foreground">{dateLabel(run.started_at)} · {run.jobs_received} received · {run.jobs_inserted} new · {run.jobs_updated} updated</p>
                {run.detail && <p className="mt-1 text-xs text-muted-foreground">{run.detail}</p>}</div>
              <Badge variant={run.complete && ["success", "empty"].includes(run.outcome) ? "secondary" : "destructive"}>{run.outcome.replaceAll("_", " ")}</Badge>
            </div>;
          })}
          {!allRuns.length && <p className="px-4 py-6 text-sm text-muted-foreground">No retrieval history is available yet.</p>}
        </div>
      </section>
    </section>
  );
}
