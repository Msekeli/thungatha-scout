import { ArrowDownRight, ArrowUpRight, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";
import { CompanyDirectoryLinks } from "./CompanyDirectoryLinks";

type Props = {
  employer: Employer;
  sources: EmployerSource[];
  currentJobs: number;
  jobChange: number;
  selected: boolean;
  onSelect: (employer: Employer) => void;
};

export function CompanyDirectoryCard({
  employer,
  sources,
  currentJobs,
  jobChange,
  selected,
  onSelect,
}: Props) {
  return (
    <article className="scout-company-card relative" data-selected={selected}>
      <div className="scout-company-card__accent" />
      {jobChange !== 0 && (
        <span
          className={
            "absolute right-4 top-5 inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold " +
            (jobChange > 0
              ? "scout-vacancy-change--positive"
              : "scout-vacancy-change--negative")
          }
          aria-label={jobChange > 0 ? `${jobChange} more jobs since last visit` : `${Math.abs(jobChange)} fewer jobs since last visit`}
        >
          {jobChange > 0 ? (
            <ArrowUpRight className="h-3.5 w-3.5" />
          ) : (
            <ArrowDownRight className="h-3.5 w-3.5" />
          )}
          {jobChange > 0 ? "+" + jobChange : jobChange}
        </span>
      )}
      <Button
        type="button"
        variant="ghost"
        aria-pressed={selected}
        onClick={() => onSelect(employer)}
        className="scout-company-card__trigger h-auto w-full items-start justify-start gap-3 rounded-none px-4 pb-3 pt-4 pr-20 text-left font-normal"
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
          <span className="mt-1 block text-xs scout-company-card__meta">
            {currentJobs} current {currentJobs === 1 ? "job" : "jobs"}
          </span>
        </span>
      </Button>
      <CompanyDirectoryLinks employer={employer} sources={sources} />
    </article>
  );
}
