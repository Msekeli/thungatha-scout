import { CalendarDays, Building2, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";

type VacancyRecordListProps = {
  vacancies: Vacancy[];
  loading: boolean;
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string) => void;
};

export function VacancyRecordList({
  vacancies,
  loading,
  selectedVacancyId,
  openingVacancyId,
  onOpenVacancy,
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
          <Button
            key={vacancy.id}
            type="button"
            variant="ghost"
            onClick={() => onOpenVacancy(vacancy.id)}
            aria-pressed={selectedVacancyId === vacancy.id}
            disabled={openingVacancyId === vacancy.id}
            data-selected={selectedVacancyId === vacancy.id}
            className="scout-vacancy-card"
          >
            <span className="scout-vacancy-card__accent" />
            <span className="scout-vacancy-card__content">
              <strong className="scout-vacancy-card__title">{vacancy.title}</strong>
              <span className="scout-vacancy-card__metadata">
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
            </span>
          </Button>
        ))
      )}
    </div>
  );
}
