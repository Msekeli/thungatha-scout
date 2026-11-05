import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";

type VacancyRecordListProps = {
  vacancies: Vacancy[];
  loading: boolean;
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string) => void;
};

const reviewLabel = (status: Vacancy["review_status"]) =>
  ({
    pending: "Pending review",
    needs_verification: "Needs verification",
    verified: "Verified",
    rejected: "Rejected",
  })[status];

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
            className={`h-auto w-full justify-start rounded-lg border p-3 text-left font-normal shadow-sm transition-all hover:border-ring hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-wait disabled:opacity-70 ${
              selectedVacancyId === vacancy.id
                ? "border-ring bg-accent shadow-sm"
                : "border-border bg-card"
            }`}
          >
            <span className="flex items-start justify-between gap-3">
              <strong className="text-sm font-semibold leading-snug text-primary">
                {vacancy.title}
              </strong>
              <Badge
                variant={
                  vacancy.review_status === "verified"
                    ? "default"
                    : vacancy.review_status === "rejected"
                      ? "destructive"
                      : "secondary"
                }
                className={
                  vacancy.review_status === "pending" ||
                  vacancy.review_status === "needs_verification"
                    ? "bg-warning-surface text-warning hover:bg-warning-surface"
                    : ""
                }
              >
                {reviewLabel(vacancy.review_status)}
              </Badge>
            </span>
            <span className="mt-1 block text-xs font-medium text-muted-foreground">
              {vacancy.employer_name}
            </span>
            <span className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-muted-foreground">
              <span>{vacancy.location_text || "Location unknown"}</span>
              {vacancy.department && <span>{vacancy.department}</span>}
              <span>
                First seen{" "}
                {new Date(vacancy.first_seen_at ?? vacancy.last_seen_at).toLocaleDateString()}
              </span>
            </span>
          </Button>
        ))
      )}
    </div>
  );
}
