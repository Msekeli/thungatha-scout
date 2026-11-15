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
    <div className="grid min-h-0 flex-1 gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(20rem,1fr)]">
      <section className="scout-company-card flex min-h-0 flex-col">
        <div className="border-b border-[var(--scout-border)] px-4 py-4">
          <h3 className="font-semibold">Company retrieval activity</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            Latest attempt for each registered source, including job changes and retrieval status.
          </p>
        </div>
        <div className="hidden border-b border-[var(--scout-border)] bg-[var(--scout-surface-raised)] px-4 py-3 text-xs font-semibold text-muted-foreground xl:grid xl:grid-cols-[minmax(11rem,1.5fr)_repeat(5,minmax(4.5rem,.65fr))_auto]">
          <span>Employer / source</span>
          <span>Active jobs</span>
          <span>New</span>
          <span>Updated</span>
          <span>Unchanged</span>
          <span>Observed Δ</span>
          <span>Status</span>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto">
          {activities.map(({ employer, sources: companySources }) => (
            <CompanyRetrievalRow
              key={employer.id}
              employer={employer}
              sources={companySources}
              runs={runs}
            />
          ))}
          {!activities.length && (
            <p className="px-4 py-8 text-sm text-muted-foreground">No registered employers yet.</p>
          )}
        </div>
      </section>
      <RecentRetrievalsPanel employers={employers} sources={sources} runs={runs} />
    </div>
  );
}
