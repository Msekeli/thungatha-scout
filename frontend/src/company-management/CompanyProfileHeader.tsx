import type { Employer } from "../api";

type Props = {
  employer: Employer;
  jobsCount: number;
};

export function CompanyProfileHeader({ employer, jobsCount }: Props) {
  return (
    <div className="scout-company-profile-header">
      <p className="scout-company-eyebrow">COMPANY</p>
      <h3 className="mt-1 text-lg font-bold scout-company-heading">{employer.name}</h3>
      <a
        href={employer.website_url ?? undefined}
        target="_blank"
        rel="noreferrer"
        className="mt-1 block truncate text-xs scout-company-link"
      >
        {employer.website_url ?? "No official website recorded"}
      </a>
      <p className="mt-3 text-sm font-medium scout-company-muted">
        {jobsCount} current {jobsCount === 1 ? "job" : "jobs"}
      </p>
    </div>
  );
}
