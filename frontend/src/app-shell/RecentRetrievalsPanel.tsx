import { Badge } from "@/components/ui/badge";
import type { Employer, EmployerSource, ExtractionRun } from "../api";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
};
const dateLabel = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : "Not recorded";

export function RecentRetrievalsPanel({ employers, sources, runs }: Props) {
  const recent = Object.values(runs)
    .flat()
    .sort((a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime())
    .slice(0, 10);
  return (
    <section className="overflow-hidden rounded-lg border bg-card">
      <div className="border-b px-4 py-3">
        <h3 className="font-semibold">Recent retrievals</h3>
      </div>
      <div className="divide-y">
        {recent.map((run) => {
          const source = sources.find((item) => item.id === run.source_id);
          const employer = employers.find((item) => item.id === source?.employer_id);
          const failed = ["transient_failure", "persistence_failure", "failed", "http_failure"].includes(run.outcome);
          const blocked = ["blocked", "rate_limited"].includes(run.outcome);\n          const partial = !failed && !blocked && (!run.complete || !["success", "empty"].includes(run.outcome));
          const unchanged = Math.max(0, run.jobs_received - run.jobs_inserted - run.jobs_updated);
          return (
            <div
              key={run.id}
              className="flex flex-wrap items-center justify-between gap-3 px-4 py-3"
            >
              <div>
                <p className="font-medium">
                  {employer?.name ?? "Unknown employer"} · {source?.adapter_key ?? "Unknown source"}
                </p>
                <p className="text-xs text-muted-foreground">
                  {dateLabel(run.started_at)} · {run.jobs_received} received · {run.jobs_inserted}{" "}
                  new · {run.jobs_updated} updated · {unchanged} unchanged
                </p>
                {run.detail && <p className="mt-1 text-xs text-muted-foreground">{run.detail}</p>}
              </div>
              <Badge variant={failed ? "destructive" : partial || blocked ? "outline" : "secondary"}>
                {run.outcome.replaceAll("_", " ")}
              </Badge>
            </div>
          );
        })}
        {!recent.length && (
          <p className="px-4 py-6 text-sm text-muted-foreground">
            No retrieval history is available yet.
          </p>
        )}
      </div>
    </section>
  );
}
