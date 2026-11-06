import { Archive, CalendarDays, Building2, MapPin, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";

type Props = {
  vacancies: Vacancy[];
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  onLoadMore: () => Promise<void>;
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  savingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string) => void;
  onArchive: (vacancy: Vacancy) => void;
  onRestore: (vacancy: Vacancy) => void;
};

export function VacancyRecordList({
  vacancies,
  loading,
  loadingMore,
  hasMore,
  onLoadMore,
  selectedVacancyId,
  openingVacancyId,
  savingVacancyId,
  onOpenVacancy,
  onArchive,
  onRestore,
}: Props) {
  return (
    <div
      className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3"
      onScroll={(event) => {
        const element = event.currentTarget;
        if (element.scrollHeight - element.scrollTop - element.clientHeight < 180)
          void onLoadMore();
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
        vacancies.map((vacancy) => {
          const archived = Boolean(vacancy.archived_at);
          const saving = savingVacancyId === vacancy.id;
          return (
            <article
              key={vacancy.id}
              className="scout-vacancy-card"
              data-selected={selectedVacancyId === vacancy.id}
            >
              <div className="flex min-w-0 items-center gap-3 px-4 py-4">
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
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  className="shrink-0"
                  disabled={saving}
                  onClick={() => (archived ? onRestore(vacancy) : onArchive(vacancy))}
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
        })
      )}
      {!loading && hasMore && (
        <div className="py-3 text-center text-xs text-muted-foreground" aria-live="polite">
          {loadingMore ? "Loading more vacancies…" : "Scroll to load more"}
        </div>
      )}
    </div>
  );
}
