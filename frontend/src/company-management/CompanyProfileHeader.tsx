import { useState } from "react";
import { Building2, BriefcaseBusiness, MapPin, Globe2 } from "lucide-react";
import type { Employer } from "../api";

type Props = {
  employer: Employer;
  jobsCount: number;
};

function formatOrganizationType(value: string): string {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function CompanyProfileHeader({ employer, jobsCount }: Props) {
  const [logoFailed, setLogoFailed] = useState(false);
  const location = [employer.city, employer.province, employer.country].filter(Boolean).join(", ");

  return (
    <section className="rounded-xl border border-border bg-card p-4 sm:p-5">
      <div className="flex min-w-0 items-start gap-4">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted/40 p-2">
          {employer.logo_url && !logoFailed ? (
            <img
              src={employer.logo_url}
              alt={`${employer.name} logo`}
              className="h-full w-full object-contain"
              onError={() => setLogoFailed(true)}
            />
          ) : (
            <Building2 className="h-8 w-8 text-muted-foreground" />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Employer profile
          </p>
          <h3 className="mt-1 break-words text-xl font-semibold leading-tight text-foreground">
            {employer.name}
          </h3>
          {employer.legal_name && employer.legal_name !== employer.name && (
            <p className="mt-1 text-sm text-muted-foreground">{employer.legal_name}</p>
          )}
          {employer.website_url ? (
            <a
              href={employer.website_url}
              target="_blank"
              rel="noreferrer"
              className="mt-2 inline-flex max-w-full items-center gap-1.5 truncate text-sm text-primary hover:underline"
            >
              <Globe2 className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{employer.website_url}</span>
            </a>
          ) : (
            <p className="mt-2 text-sm text-muted-foreground">No official website recorded</p>
          )}
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 gap-3 border-t border-border pt-4 sm:grid-cols-2">
        <div className="flex min-w-0 items-start gap-2.5">
          <BriefcaseBusiness className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">Current vacancies</p>
            <p className="mt-0.5 text-sm font-medium text-foreground">
              {jobsCount} {jobsCount === 1 ? "job" : "jobs"}
            </p>
          </div>
        </div>
        <div className="flex min-w-0 items-start gap-2.5">
          <Building2 className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">Organisation type</p>
            <p className="mt-0.5 text-sm font-medium text-foreground">
              {formatOrganizationType(employer.organization_type || "unresolved")}
            </p>
          </div>
        </div>
        <div className="flex min-w-0 items-start gap-2.5 sm:col-span-2">
          <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="min-w-0">
            <p className="text-xs text-muted-foreground">Location</p>
            <p className="mt-0.5 text-sm font-medium text-foreground">
              {location || "No location recorded"}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
