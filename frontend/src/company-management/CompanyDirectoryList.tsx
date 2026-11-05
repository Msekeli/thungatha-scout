import type { FC } from "react";
import { Building2, ExternalLink, Globe2, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  selectedEmployerId: string;
  onSelectEmployer: (employer: Employer) => void;
  emptyMessage?: string;
};

export const CompanyDirectoryList: FC<Props> = ({
  employers,
  sources,
  selectedEmployerId,
  onSelectEmployer,
  emptyMessage = "No companies matched your criteria.",
}) => {
  if (!employers.length)
    return (
      <div className="rounded-xl border border-dashed border-border py-12 text-center text-sm text-muted-foreground">
        {emptyMessage}
      </div>
    );
  return (
    <div className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
      {employers.map((employer) => {
        const companySources = sources.filter((source) => source.employer_id === employer.id);
        const selected = selectedEmployerId === employer.id;
        return (
          <article
            key={employer.id}
            className={`group min-w-0 overflow-hidden rounded-xl border bg-card shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md ${selected ? "border-primary ring-1 ring-primary/30" : "border-border"}`}
          >
            <Button
              type="button"
              variant="ghost"
              aria-pressed={selected}
              onClick={() => onSelectEmployer(employer)}
              className="h-auto w-full items-start justify-start gap-3 rounded-none p-3 text-left font-normal hover:bg-primary/5"
            >
              {employer.logo_url ? (
                <img
                  src={employer.logo_url}
                  alt=""
                  className="h-11 w-11 shrink-0 rounded-lg border border-border bg-white object-contain p-1"
                />
              ) : (
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary">
                  <Building2 className="h-5 w-5" />
                </span>
              )}
              <span className="min-w-0 flex-1">
                <strong className="block truncate text-sm font-semibold text-foreground">
                  {employer.name}
                </strong>
                <span className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                  <MapPin className="h-3 w-3 shrink-0" />
                  <span className="truncate">
                    {[employer.city, employer.province].filter(Boolean).join(", ") ||
                      "Location not recorded"}
                  </span>
                </span>
                <span className="mt-2 flex flex-wrap gap-1">
                  <Badge variant="secondary" className="text-[10px] capitalize">
                    {employer.organization_type.replaceAll("_", " ")}
                  </Badge>
                  <Badge variant="outline" className="text-[10px] capitalize">
                    {employer.status.replaceAll("_", " ")}
                  </Badge>
                  <Badge variant="outline" className="text-[10px]">
                    {companySources.length} source{companySources.length === 1 ? "" : "s"}
                  </Badge>
                </span>
              </span>
            </Button>
            <div className="flex flex-wrap gap-x-3 gap-y-1 border-t border-border bg-muted/30 px-3 py-2">
              {employer.website_url && (
                <a
                  href={employer.website_url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(event) => event.stopPropagation()}
                  className="inline-flex min-w-0 items-center gap-1 text-[11px] text-primary hover:underline"
                >
                  <Globe2 className="h-3 w-3 shrink-0" /> Official website
                  <ExternalLink className="h-3 w-3 shrink-0" />
                </a>
              )}
              {companySources.map((source) => (
                <a
                  key={source.id}
                  href={source.source_url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(event) => event.stopPropagation()}
                  className="inline-flex min-w-0 items-center gap-1 text-[11px] text-primary hover:underline"
                >
                  {source.adapter_key} careers <ExternalLink className="h-3 w-3 shrink-0" />
                </a>
              ))}
              {!employer.website_url && !companySources.length && (
                <span className="text-[11px] text-muted-foreground">
                  No official links recorded
                </span>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
};
