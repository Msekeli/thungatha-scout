import { ArrowDownRight, ArrowUpRight, Building2, BriefcaseBusiness } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { CompanyDirectoryLinks } from "./CompanyDirectoryLinks";

type Props = {
  employer: Employer;
  sources: EmployerSource[];
  extractionRuns: Record<string, ExtractionRun[]>;
  selected: boolean;
  onSelect: (employer: Employer) => void;
};

export function CompanyDirectoryCard({
  employer,
  sources,
  extractionRuns,
  selected,
  onSelect,
}: Props) {
  const runGroups = sources.map((source) =>
    (extractionRuns[source.id] ?? [])
      .filter((run) => run.complete && ["success", "empty"].includes(run.outcome))
      .sort(
        (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
      ),
  );
  const comparable = runGroups.length > 0 && runGroups.every((runs) => runs.length > 1);
  const change = comparable
    ? runGroups.reduce((total, runs) => total + runs[0].jobs_received - runs[1].jobs_received, 0)
    : null;
  return (
    <article className="scout-company-card" data-selected={selected}>
      <div className="scout-company-card__accent" />
      <Button
        type="button"
        variant="ghost"
        aria-pressed={selected}
        onClick={() => onSelect(employer)}
        className="scout-company-card__trigger h-auto w-full items-start justify-start gap-3 rounded-none px-4 pb-3 pt-4 text-left font-normal"
      >
        <span className="scout-company-card__icon">
          {employer.logo_url ? (
            <img src={employer.logo_url} alt="" className="scout-company-card__logo" />
          ) : (
            <Building2 className="h-5 w-5" />
          )}
        </span>
        <span className="min-w-0 flex-1">
          <strong className="block truncate text-sm font-semibold scout-company-card__name">
            {employer.name}
          </strong>
          <span className="mt-1 flex items-center gap-2 text-xs scout-company-card__meta">
            <BriefcaseBusiness className="h-3.5 w-3.5 scout-company-card__meta" />
            {sources.length} registered source{sources.length === 1 ? "" : "s"}
          </span>
          {change !== null && (
            <span
              className={
                "mt-2 inline-flex items-center gap-1 text-xs font-semibold scout-vacancy-change--" +
                (change > 0 ? "positive" : change < 0 ? "negative" : "neutral")
              }
            >
              {change > 0 ? (
                <ArrowUpRight className="h-3.5 w-3.5" />
              ) : change < 0 ? (
                <ArrowDownRight className="h-3.5 w-3.5" />
              ) : null}
              {change > 0 ? "+" + change : change} jobs since previous run
            </span>
          )}
        </span>
      </Button>
      <CompanyDirectoryLinks employer={employer} sources={sources} />
    </article>
  );
}
