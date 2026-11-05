import { Ban, CalendarDays, Building2, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";

type VacancyRecordListProps = {
  vacancies: Vacancy[];
  loading: boolean;
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string) => void;
  onExcludeVacancy: (vacancyId: string) => Promise<void>;
};

export function VacancyRecordList({
  vacancies,
  loading,
  selectedVacancyId,
  openingVacancyId,
  onOpenVacancy,
  onExcludeVacancy,
}: VacancyRecordListProps) {
  return (
    <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
      {loading ? (
        <p className="py-12 text-center text-sm text-muted-foreground">Loading operational data…</p>
      ) : vacancies.length === 0 ? (
        <div className="py-12 text-center">
          <p className="text-sm font-semibold">No matching records</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Adjust the filters or register a source.
          </p>
        </div>
      ) : (
        vacancies.map((vacancy) => (
          <article
            key={vacancy.id}
            className="scout-vacancy-card"
            data-selected={selectedVacancyId === vacancy.id}
          >
            <div className="flex min-w-0 items-start gap-2 px-4 py-4">
              <button
                type="button"
                className="min-w-0 flex-1 text-left"
                onClick={() => onOpenVacancy(vacancy.id)}
                aria-pressed={selectedVacancyId === vacancy.id}
                disabled={openingVacancyId === vacancy.id}
              >
                <strong className="scout-vacancy-card__title">{vacancy.title}</strong>
                <span className="scout-vacancy-card__metadata mt-3">
                  <span>
                    <Building2 aria-hidden="true" />
                    {vacancy.employer_name}
                  </span>
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
              {vacancy.review_status !== "rejected" && (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="scout-vacancy-card__exclude"
                  aria-label={"Exclude " + vacancy.title + " from Thungatha publication"}
                  title="Exclude from publication"
                  onClick={() => {
                    const confirmed = window.confirm(
                      "Exclude this vacancy from Thungatha? It will remain in Scout, but it will not be published to Thungatha.",
                    );
                    if (confirmed) void onExcludeVacancy(vacancy.id);
                  }}
                >
                  <Ban className="h-4 w-4" />
                </Button>
              )}
            </div>
          </article>
        ))
      )}
    </div>
  );
}
