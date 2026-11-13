import { AlertTriangle, CheckCircle2, Clock3 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { ExtractionRun } from "../api";

type Props = { runs: ExtractionRun[] };

const isFailure = (run: ExtractionRun) =>
  ["transient_failure", "persistence_failure", "failed", "http_failure"].includes(run.outcome);
const isBlocked = (run: ExtractionRun) => ["blocked", "rate_limited"].includes(run.outcome);
const isPartial = (run: ExtractionRun) =>
  !isFailure(run) && !isBlocked(run) && (!run.complete || !["success", "empty"].includes(run.outcome));

export function RetrievalScheduleCard({ runs }: Props) {
  const failed = runs.filter(isFailure).length;
  const blocked = runs.filter(isBlocked).length;
  const partial = runs.filter(isPartial).length;
  const noChanges = runs.filter(
    (run) => run.complete && run.jobs_inserted === 0 && run.jobs_updated === 0 && run.jobs_received > 0,
  ).length;
  const latest = [...runs].sort(
    (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
  )[0];
  return (
    <div className="grid shrink-0 gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
      <section className="rounded-lg border bg-card p-4">
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-semibold">Automatic retrieval</h3>
          <Badge variant="secondary">Not active</Badge>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">Target cadence: every 12 hours.</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Scheduling is not connected. Manual retrieval is available; no next-run time is currently known.
        </p>
      </section>
      <section className="rounded-lg border bg-card p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-semibold">Retrieval health</h3>
          <span className="text-xs text-muted-foreground">Loaded history: up to 20 runs per source</span>
        </div>
        <div className="mt-3 grid gap-3 sm:grid-cols-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-destructive" />
            <div><p className="text-xl font-semibold tabular-nums">{failed}</p><p className="text-xs text-muted-foreground">Failed</p></div>
          </div>
          <div className="flex items-center gap-2">
            <Clock3 className="h-4 w-4 text-muted-foreground" />
            <div><p className="text-xl font-semibold tabular-nums">{partial}</p><p className="text-xs text-muted-foreground">Partial / unresolved</p></div>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            <div><p className="text-xl font-semibold tabular-nums">{noChanges}</p><p className="text-xs text-muted-foreground">Completed, no changes</p></div>
          </div>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          {latest?.started_at
            ? `Most recent attempt: ${new Date(latest.started_at).toLocaleString()}`
            : "No extraction runs have been recorded."}
        </p>
      </section>
    </div>
  );
}
