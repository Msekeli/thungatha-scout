import { Badge } from "@/components/ui/badge";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { RecentRetrievalsPanel } from "./RecentRetrievalsPanel";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
};
type CompanyActivity = {
  employer: Employer;
  sources: EmployerSource[];
  latest: ExtractionRun[];
  previous: ExtractionRun[];
  observedDelta: number;
  hasComparison: boolean;
};
const dateLabel = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : "Not recorded";

function statusFor(runs: ExtractionRun[]) {
  if (runs.some((run) => ["transient_failure", "persistence_failure", "failed", "blocked"].includes(run.outcome))) {
    return { label: "Failed", variant: "destructive" as const };
  }
  if (runs.some((run) => !run.complete || !["success", "empty"].includes(run.outcome))) {
    return { label: "Partial", variant: "outline" as const };
  }
  if (runs.length && runs.every((run) => run.outcome === "empty" || (run.jobs_inserted === 0 && run.jobs_updated === 0))) {
    return { label: "No changes", variant: "secondary" as const };
  }
  return { label: "Retrieved", variant: "secondary" as const };
}

function buildActivity(employers: Employer[], sources: EmployerSource[], runs: Props["runs"]) {
  return employers.map((employer) => {
    const companySources = sources.filter((source) => source.employer_id === employer.id);
    const latest: ExtractionRun[] = [];
    const previous: ExtractionRun[] = [];
    let observedDelta = 0;
    let hasComparison = false;
    companySources.forEach((source) => {
      const history = [...(runs[source.id] ?? [])].sort(
        (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
      );
      if (history[0]) latest.push(history[0]);
      const latestComplete = history[0]?.complete && ["success", "empty"].includes(history[0].outcome);
      const previousComplete = history.slice(1).find(
        (run) => run.complete && ["success", "empty"].includes(run.outcome),
      );
      if (previousComplete) previous.push(previousComplete);
      if (latestComplete && previousComplete) {
        observedDelta += history[0].jobs_received - previousComplete.jobs_received;
        hasComparison = true;
      }
    });
    return { employer, sources: companySources, latest, previous, observedDelta, hasComparison };
  }).sort((a, b) => {
    const aDate = Math.max(...a.latest.map((run) => new Date(run.started_at ?? 0).getTime()), 0);
    const bDate = Math.max(...b.latest.map((run) => new Date(run.started_at ?? 0).getTime()), 0);
    return bDate - aDate;
  });
}

function CompanyRow({ activity }: { activity: CompanyActivity }) {
  const { employer, sources, latest, previous } = activity;
  const received = latest.reduce((sum, run) => sum + run.jobs_received, 0);
  const added = latest.reduce((sum, run) => sum + run.jobs_inserted, 0);
  const updated = latest.reduce((sum, run) => sum + run.jobs_updated, 0);
  const unchanged = Math.max(0, received - added - updated);
  const { observedDelta, hasComparison } = activity;
  const status = latest.length ? statusFor(latest) : { label: "Never retrieved", variant: "outline" as const };
  const lastAttempt = latest.map((run) => run.started_at ?? "").sort().slice(-1)[0];
  return (
    <div className="grid gap-3 border-b px-4 py-3 last:border-b-0 xl:grid-cols-[minmax(12rem,1.5fr)_repeat(5,minmax(5rem,.65fr))_auto] xl:items-center">
      <div className="min-w-0">
        <p className="truncate font-medium">{employer.name}</p>
        <p className="truncate text-xs text-muted-foreground">
          {sources.length ? sources.map((source) => source.adapter_key).join(", ") : "No registered source"}
        </p>
        <p className="text-xs text-muted-foreground">{dateLabel(lastAttempt)}</p>
      </div>
      <Metric label="Tracked jobs" value={employer.vacancy_count ?? "—"} />
      <Metric label="New this run" value={added} />
      <Metric label="Updated" value={updated} />
      <Metric label="Unchanged" value={unchanged} />
      <div>
        <p className="text-xs text-muted-foreground">Observed change</p>
        <p className={hasPrior && delta !== 0 ? "font-semibold tabular-nums" : "font-medium tabular-nums"}>
          {hasPrior ? `${delta > 0 ? "+" : ""}${delta}` : "—"}
        </p>
      </div>
      <Badge variant={status.variant}>{status.label}</Badge>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number | string }) {
  return <div><p className="text-xs text-muted-foreground">{label}</p><p className="font-medium tabular-nums">{value}</p></div>;
}

export function SourceStatusPanel({ employers, sources, runs }: Props) {
  const activities = buildActivity(employers, sources, runs);
  return (
    <section className="overflow-hidden rounded-lg border bg-card">
      <div className="border-b px-4 py-3">
        <h3 className="font-semibold">Company retrieval activity</h3>
        <p className="text-sm text-muted-foreground">
          Latest attempt per source. New and updated counts come from that run; observed jobs change compares successful runs only.
        </p>
      </div>
      <div className="hidden border-b bg-muted/40 px-4 py-2 text-xs font-medium text-muted-foreground xl:grid xl:grid-cols-[minmax(12rem,1.5fr)_repeat(5,minmax(5rem,.65fr))_auto]">
        <span>Company / source</span><span>Tracked jobs</span><span>New this run</span>
        <span>Updated</span><span>Unchanged</span><span>Observed jobs Δ</span><span>Status</span>
      </div>
      {activities.map((activity) => <CompanyRow key={activity.employer.id} activity={activity} />)}
      {!activities.length && <p className="px-4 py-6 text-sm text-muted-foreground">No registered employers yet.</p>}
    </section>
    <RecentRetrievalsPanel employers={employers} sources={sources} runs={runs} />
  );
}
