import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { CompanyRetrievalRow } from "./CompanyRetrievalRow";
import { RecentRetrievalsPanel } from "./RecentRetrievalsPanel";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
};

export function SourceStatusPanel({ employers, sources, runs }: Props) {
  const activities = employers
    .map((employer) => ({
      employer,
      sources: sources.filter((source) => source.employer_id === employer.id),
    }))
    .sort((a, b) => a.employer.name.localeCompare(b.employer.name));
  return (
    <>
      <section className="overflow-hidden rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">Company retrieval activity</h3>
          <p className="text-sm text-muted-foreground">
            Latest attempt per source. New and updated counts come from that run; observed jobs
            change compares successful runs only.
          </p>
        </div>
        <div className="hidden border-b bg-muted/40 px-4 py-2 text-xs font-medium text-muted-foreground xl:grid xl:grid-cols-[minmax(12rem,1.5fr)_repeat(5,minmax(5rem,.65fr))_auto]">
          <span>Company / source</span>
          <span>Tracked jobs</span>
          <span>New this run</span>
          <span>Updated</span>
          <span>Unchanged</span>
          <span>Observed jobs Δ</span>
          <span>Status</span>
        </div>
        {activities.map(({ employer, sources: companySources }) => (
          <CompanyRetrievalRow
            key={employer.id}
            employer={employer}
            sources={companySources}
            runs={runs}
          />
        ))}
        {!activities.length && (
          <p className="px-4 py-6 text-sm text-muted-foreground">No registered employers yet.</p>
        )}
      </section>
      <RecentRetrievalsPanel employers={employers} sources={sources} runs={runs} />
    </>
  );
}
