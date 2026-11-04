import { Badge } from "@/components/ui/badge";
import type { ExtractionRun } from "../api";

type ExtractionRunHistoryProps = {
  runs: ExtractionRun[];
};

export function ExtractionRunHistory({ runs }: ExtractionRunHistoryProps) {
  if (runs.length === 0) {
    return <p className="text-xs text-muted-foreground">No extraction runs recorded yet.</p>;
  }

  const latestRun = runs[0];
  const successful = ["success", "empty"].includes(latestRun.outcome);
  const failed = ["not_found", "blocked", "malformed", "persistence_failure"].includes(
    latestRun.outcome,
  );

  return (
    <div className="grid gap-2 rounded-lg border border-border bg-muted/50 p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <strong className="text-xs font-semibold text-foreground">Latest extraction</strong>
        <span className="text-[10px] text-muted-foreground">{runs.length} recorded run(s)</span>
      </div>
      <div className="flex flex-wrap items-center gap-2 text-[10px] text-muted-foreground">
        <Badge
          variant={successful ? "default" : failed ? "destructive" : "secondary"}
          className="capitalize"
        >
          {latestRun.outcome.replaceAll("_", " ")}
        </Badge>
        <span>
          {latestRun.jobs_received} received · {latestRun.jobs_inserted} new ·{" "}
          {latestRun.jobs_updated} updated
        </span>
        <span>{latestRun.complete ? "Complete" : "Incomplete"}</span>
      </div>
      {latestRun.detail && (
        <p
          className={
            successful
              ? "break-words text-[10px] leading-relaxed text-muted-foreground"
              : "break-words text-[10px] leading-relaxed text-destructive"
          }
        >
          {latestRun.detail}
        </p>
      )}
      <div className="flex flex-wrap justify-between gap-2 text-[10px] text-muted-foreground">
        <span>
          Started:{" "}
          {latestRun.started_at ? new Date(latestRun.started_at).toLocaleString() : "Unknown"}
        </span>
        <span>
          Finished:{" "}
          {latestRun.finished_at ? new Date(latestRun.finished_at).toLocaleString() : "Not finished"}
        </span>
      </div>
      {runs.length > 1 && (
        <details className="border-t border-border pt-2 text-xs">
          <summary className="cursor-pointer font-semibold text-muted-foreground">
            Previous runs ({runs.length - 1})
          </summary>
          <div className="divide-y divide-border">
            {runs.slice(1).map((run) => (
              <div key={run.id} className="grid gap-1 py-2">
                <strong className="capitalize text-foreground">
                  {run.outcome.replaceAll("_", " ")}
                </strong>
                <span className="text-muted-foreground">
                  {run.jobs_received} received · {run.jobs_inserted} new · {run.jobs_updated} updated
                </span>
                <small className="text-muted-foreground">
                  {run.detail || "No additional detail"}
                </small>
                <small className="text-muted-foreground">
                  {run.started_at ? new Date(run.started_at).toLocaleString() : "Unknown time"}
                </small>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
