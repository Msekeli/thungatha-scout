import { Badge } from "@/components/ui/badge";
import type { Employer, EmployerSource, ExtractionRun } from "../api";

type Props = {
  employer: Employer;
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
};
const dateLabel = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : "Not recorded";
const failedOutcomes = ["transient_failure", "persistence_failure", "failed", "http_failure"];
const blockedOutcomes = ["blocked", "rate_limited"];
const goodRun = (run: ExtractionRun) => run.complete && ["success", "empty"].includes(run.outcome);

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-medium tabular-nums">{value}</p>
    </div>
  );
}

export function CompanyRetrievalRow({ employer, sources, runs }: Props) {
  const latest: ExtractionRun[] = [];
  let observedDelta = 0;
  let hasComparison = false;
  sources.forEach((source) => {
    const history = [...(runs[source.id] ?? [])].sort(
      (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
    );
    const current = history[0];
    if (!current) return;
    latest.push(current);
    const previous = history.slice(1).find(goodRun);
    if (goodRun(current) && previous) {
      observedDelta += current.jobs_received - previous.jobs_received;
      hasComparison = true;
    }
  });
  const received = latest.reduce((sum, run) => sum + run.jobs_received, 0);
  const added = latest.reduce((sum, run) => sum + run.jobs_inserted, 0);
  const updated = latest.reduce((sum, run) => sum + run.jobs_updated, 0);
  const unchanged = Math.max(0, received - added - updated);
  const failed = latest.some((run) => failedOutcomes.includes(run.outcome));
  const blocked = !failed && latest.some((run) => blockedOutcomes.includes(run.outcome));
  const partial = !failed && !blocked && latest.some((run) => !goodRun(run));
  const noChanges =
    latest.length > 0 && latest.every((run) => goodRun(run)) && added === 0 && updated === 0;
  const status = !latest.length
    ? "Never retrieved"
    : failed
      ? "Failed"
      : blocked
        ? "Blocked / limited"
        : partial
          ? "Partial"
          : noChanges
            ? "No changes"
            : "Retrieved";
  const variant = failed
    ? "destructive"
    : partial || blocked || !latest.length
      ? "outline"
      : "secondary";
  const lastAttempt = latest
    .map((run) => run.started_at ?? "")
    .sort()
    .slice(-1)[0];
  return (
    <div className="grid gap-3 border-b px-4 py-3 last:border-b-0 xl:grid-cols-[minmax(12rem,1.5fr)_repeat(5,minmax(5rem,.65fr))_auto] xl:items-center">
      <div className="min-w-0">
        <p className="truncate font-medium">{employer.name}</p>
        <p className="truncate text-xs text-muted-foreground">
          {sources.map((source) => source.adapter_key).join(", ") || "No registered source"}
        </p>
        <p className="text-xs text-muted-foreground">{dateLabel(lastAttempt)}</p>
      </div>
      <Metric label="Active jobs" value={employer.vacancy_count ?? "—"} />
      <Metric label="New this run" value={added} />
      <Metric label="Updated" value={updated} />
      <Metric label="Unchanged" value={unchanged} />
      <Metric
        label="Observed jobs Δ"
        value={hasComparison ? `${observedDelta > 0 ? "+" : ""}${observedDelta}` : "—"}
      />
      <Badge variant={variant}>{status}</Badge>
    </div>
  );
}
