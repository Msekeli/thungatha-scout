import { Badge } from "@/components/ui/badge";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { RecentRetrievalsPanel } from "./RecentRetrievalsPanel";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
};
const dateLabel = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : "Not recorded";

export function SourceStatusPanel({ employers, sources, runs }: Props) {
  return (
    <>
      <section className="overflow-hidden rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">Source status</h3>
        </div>
        <div className="divide-y">
          {sources.map((source) => {
            const run = runs[source.id]?.[0];
            const employer = employers.find((item) => item.id === source.employer_id);
            const healthy = run?.complete && ["success", "empty"].includes(run.outcome);
            return (
              <div
                key={source.id}
                className="grid gap-2 px-4 py-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-center"
              >
                <div className="min-w-0">
                  <p className="truncate font-medium">{employer?.name ?? "Unknown employer"}</p>
                  <p className="truncate text-sm text-muted-foreground">
                    {source.adapter_key} · {source.source_url}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Last attempt: {dateLabel(run?.started_at)}
                  </p>
                  {typeof source.discovery_preview?.crawl_complete === "boolean" && (
                    <p className="text-xs text-muted-foreground">
                      Career page: {source.discovery_preview.pages_observed ?? 0} pages ·{" "}
                      {source.discovery_preview.vacancies_found ?? 0} vacancies ·{" "}
                      {source.discovery_preview.failed_urls?.length ?? 0} failed URLs ·{" "}
                      {source.discovery_preview.crawl_complete ? "complete" : "incomplete"}
                    </p>
                  )}
                </div>
                <Badge variant={!run ? "outline" : healthy ? "secondary" : "destructive"}>
                  {!run ? "Never retrieved" : run.outcome.replaceAll("_", " ")}
                </Badge>
              </div>
            );
          })}
          {!sources.length && (
            <p className="px-4 py-6 text-sm text-muted-foreground">No registered sources yet.</p>
          )}
        </div>
      </section>
      <RecentRetrievalsPanel employers={employers} sources={sources} runs={runs} />
    </>
  );
}
