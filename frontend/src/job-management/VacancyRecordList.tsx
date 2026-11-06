import { CalendarDays, Building2, MapPin } from "lucide-react";
import type { Vacancy } from "../api";

type VacancyRecordListProps = {
  vacancies: Vacancy[];
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  onLoadMore: () => Promise<void>;
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string) => void;
};

export function VacancyRecordList({
  vacancies,
  loading,
  loadingMore,
  hasMore,
  onLoadMore,
  selectedVacancyId,
  openingVacancyId,
  onOpenVacancy,
}: VacancyRecordListProps) {
  return (
    <div
      className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3"
      onScroll={(event) => {
        const element = event.currentTarget;
        if (element.scrollHeight - element.scrollTop - element.clientHeight < 180) {
          void onLoadMore();
        }
      }}
    >
      {loading && vacancies.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">Loading vacancies…</p>
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
            </div>
          </article>
        ))
      )}
      {!loading && hasMore && (
        <div className="py-3 text-center text-xs text-muted-foreground" aria-live="polite">
          {loadingMore ? "Loading more vacancies…" : "Scroll to load more"}
        </div>
      )}
    </div>
  );
}
