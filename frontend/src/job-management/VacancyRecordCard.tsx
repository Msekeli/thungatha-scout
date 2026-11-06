import { Archive, CalendarDays, Building2, MapPin, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";
import { getCompanyIconUrl } from "../company-management/company-icon-url";

type Props = {
  vacancy: Vacancy;
  selected: boolean;
  opening: boolean;
  saving: boolean;
  onOpen: () => void;
  onArchive: () => void;
  onRestore: () => void;
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
  const logoUrl =
    vacancy.employer_logo_url ||
    getCompanyIconUrl(vacancy.employer_website_url || vacancy.employer_careers_url);
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
            <span className="scout-vacancy-card__employer-logo">
              {logoUrl ? (
                <img
                  src={logoUrl}
                  alt=""
                  onError={(event) => {
                    event.currentTarget.style.display = "none";
                  }}
                />
              ) : (
                <Building2 aria-hidden="true" />
              )}
            </span>
            <span className="min-w-0">
              <strong className="scout-vacancy-card__title">{vacancy.title}</strong>
              <span className="block text-xs text-muted-foreground">{vacancy.employer_name}</span>
            </span>
          </span>
          <span className="scout-vacancy-card__metadata mt-3">
            <span>
              <MapPin aria-hidden="true" />
              {vacancy.location_text || "Location unknown"}
            </span>
            <span>
              <CalendarDays aria-hidden="true" />
              {new Date(vacancy.first_seen_at ?? vacancy.last_seen_at).toLocaleDateString()}
            </span>
          </span>
        </button>
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="shrink-0"
          disabled={saving}
          onClick={archived ? onRestore : onArchive}
          aria-label={archived ? "Reinstate vacancy" : "Archive vacancy"}
        >
          {archived ? (
            <RotateCcw className="mr-1.5 h-3.5 w-3.5" />
          ) : (
            <Archive className="mr-1.5 h-3.5 w-3.5" />
          )}
          {archived ? "Reinstate" : "Archive"}
        </Button>
      </div>
    </article>
  );
}
