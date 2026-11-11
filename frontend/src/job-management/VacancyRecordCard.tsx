import { CalendarDays, MapPin } from "lucide-react";
import type { Vacancy } from "../api";
import { EmployerBrandMark } from "../company-management/employer-brand-mark";
import { isApprovedEmployerBranding } from "../company-management/company-icon-url";
import { getVacancyFreshness } from "./vacancy-freshness";
import { VacancyRecordCardActions } from "./vacancy-record-card-actions";

type Props = {
  vacancy: Vacancy;
  selected: boolean;
  opening: boolean;
  saving: boolean;
  onOpen: () => void;
  onArchive: () => void;
  onRestore: () => void;
};
const freshnessColor = {
  fresh: "text-emerald-400",
  recent: "text-yellow-300",
  aging: "text-amber-400",
  stale: "text-red-400",
};

export function VacancyRecordCard({
  vacancy,
  selected,
  opening,
  saving,
  onOpen,
  onArchive,
  onRestore,
}: Props) {
  const archived = Boolean(vacancy.archived_at);
  const freshness = getVacancyFreshness(vacancy.source_updated_at, vacancy.published_at);
  const logoUrl = isApprovedEmployerBranding(
    vacancy.employer_logo_url,
    vacancy.employer_logo_type,
    vacancy.employer_logo_source_url,
    vacancy.employer_website_url,
  )
    ? vacancy.employer_logo_url
    : null;
  return (
    <article className="scout-vacancy-card" data-selected={selected}>
      <div className="flex min-w-0 items-center gap-3 px-4 py-4">
        <button
          type="button"
          className="min-w-0 flex-1 text-left"
          onClick={onOpen}
          aria-pressed={selected}
          disabled={opening}
        >
          <span className="flex items-center gap-3">
            <EmployerBrandMark
              name={vacancy.employer_name}
              logoUrl={logoUrl}
              className="scout-vacancy-card__employer-logo"
              logoClassName="h-9 w-9 rounded-lg bg-white object-contain p-1"
            />
            <span className="min-w-0 flex-1">
              <strong className="scout-vacancy-card__title">{vacancy.title}</strong>
              <span className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                <span className="font-medium">{vacancy.employer_name}</span>
                <span className="scout-vacancy-card__metadata">
                  <MapPin aria-hidden="true" />
                  {vacancy.location_text || "Location unknown"}
                </span>
                <span className="inline-flex items-center gap-1.5">
                  <CalendarDays aria-hidden="true" className="h-3.5 w-3.5 text-muted-foreground" />
                  <span>{freshness?.dateLabel ?? "Date not stated"}</span>
                  {freshness && (
                    <strong className={"font-semibold " + freshnessColor[freshness.tone]}>
                      {freshness.ageLabel}
                    </strong>
                  )}
                </span>
              </span>
            </span>
          </span>
        </button>
        <VacancyRecordCardActions
          archived={archived}
          saving={saving}
          onArchive={onArchive}
          onRestore={onRestore}
        />
      </div>
    </article>
  );
}
