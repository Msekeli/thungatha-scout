import { Badge } from "@/components/ui/badge";
import type { Employer, EmployerSource, ExtractionRun } from "../api";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
};

const dateLabel = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : "Not recorded";

const failedOutcomes = [
  "transient_failure",
  "persistence_failure",
  "failed",
  "http_failure",
];
const blockedOutcomes = ["blocked", "rate_limited"];

export function RecentRetrievalsPanel({ employers, sources, runs }: Props) {
  const recent = Object.values(runs)
    .flat()
    .sort(
      (a, b) =>
        new Date(b.started_at ?? 0).getTime() -
        new Date(a.started_at ?? 0).getTime(),
    )
    .slice(0, 10);

  return (
    <section className="scout-company-card flex min-h-0 flex-col">
      <div className="border-b border-[var(--scout-border)] px-4 py-4">
        <h3 className="font-semibold">Recent retrievals</h3>
        <p className="mt-1 text-xs text-muted-foreground">
          The latest 10 attempts across all configured sources.
        </p>
      </div>
      <div className="min-h-0 flex-1 divide-y divide-[var(--scout-border)] overflow-y-auto">
        {recent.map((run) => {
          const source = sources.find((item) => item.id === run.source_id);
          const employer = employers.find(
            (item) => item.id === source?.employer_id,
          );
          const failed = failedOutcomes.includes(run.outcome);
          const blocked = blockedOutcomes.includes(run.outcome);
          const partial =
            !failed &&
            !blocked &&
            (!run.complete || !["success", "empty"].includes(run.outcome));
          const unchanged = Math.max(
            0,
            run.jobs_received - run.jobs_inserted - run.jobs_updated,
          );
          const variant = failed
            ? "destructive"
            : blocked || partial
              ? "outline"
              : "secondary";

          return (
            <div key={run.id} className="space-y-2 px-4 py-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">
                    {employer?.name ?? "Unknown employer"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {source?.adapter_key ?? "Unknown source"} ·{" "}
                    {dateLabel(run.started_at)}
                  </p>
                </div>
                <Badge variant={variant}>
                  {run.outcome.replaceAll("_", " ")}
                </Badge>
              </div>
              <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground">
                <span>{run.jobs_received} received</span>
                <span>{run.jobs_inserted} new</span>
                <span>{run.jobs_updated} updated</span>
                <span>{unchanged} unchanged</span>
              </div>
              {run.detail && (
                <p className="text-xs text-muted-foreground">{run.detail}</p>
              )}
            </div>
          );
        })}
        {!recent.length && (
          <p className="px-4 py-8 text-sm text-muted-foreground">
            No retrieval history is available yet.
          </p>
        )}
      </div>
    </section>
  );
}
