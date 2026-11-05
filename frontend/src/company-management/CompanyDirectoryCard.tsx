import { Building2, BriefcaseBusiness } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";
import { CompanyDirectoryLinks } from "./CompanyDirectoryLinks";

type Props = {
  employer: Employer;
  sources: EmployerSource[];
  selected: boolean;
  onSelect: (employer: Employer) => void;
};

export function CompanyDirectoryCard({ employer, sources, selected, onSelect }: Props) {
  return (
    <article
      className="scout-company-card" data-selected={selected}
    >
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
            <img
              src={employer.logo_url}
              alt=""
              className="scout-company-card__logo"
            />
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
          <span className="mt-3 flex flex-wrap gap-1.5">
            <Badge className="scout-status scout-status--type">
              {employer.organization_type.replaceAll("_", " ")}
            </Badge>
            <Badge className={`scout-status ${employer.status === "approved" ? "scout-status--approved" : employer.status === "rejected" ? "scout-status--rejected" : "scout-status--review"}`}>
              {employer.status.replaceAll("_", " ")}
            </Badge>
          </span>
        </span>
      </Button>
      <CompanyDirectoryLinks employer={employer} sources={sources} />
    </article>
  );
}
