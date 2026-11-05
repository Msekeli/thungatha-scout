import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";

const reviewLabel = (status: Vacancy["review_status"]) =>
  ({ pending: "Pending review", needs_verification: "Needs verification", verified: "Verified", rejected: "Rejected" })[status];

export function VacancyDetailsHeader({ vacancy, onClear }: {
  vacancy: Vacancy;
  onClear: () => void;
}) {
  return (
    <>
      <div className="flex items-center justify-between gap-3 border-b border-border bg-card p-4 text-card-foreground">
        <div className="min-w-0">
          <p className="text-[10px] font-medium text-scout-cyan">
            {vacancy.employer_name} · {vacancy.location_text || "Location unknown"}
          </p>
          <h3 className="mt-1 text-sm font-bold">{vacancy.title}</h3>
        </div>
        <Button type="button" variant="ghost" size="sm" className="text-muted-foreground hover:bg-accent hover:text-accent-foreground" onClick={onClear}>
          Clear
        </Button>
      </div>
      <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-3">
        <Button asChild type="button" size="sm" className="bg-scout-cyan text-primary hover:opacity-90">
          <a href={vacancy.application_url} target="_blank" rel="noreferrer">Open source listing ↗</a>
        </Button>
        <Button asChild size="sm" variant="outline">
          <a href={vacancy.source_url} target="_blank" rel="noreferrer">Source record ↗</a>
        </Button>
        <Badge
          variant={vacancy.review_status === "verified" ? "default" : vacancy.review_status === "rejected" ? "destructive" : "secondary"}
          className={vacancy.review_status === "pending" || vacancy.review_status === "needs_verification" ? "bg-warning-surface text-warning hover:bg-warning-surface" : ""}
        >
          {reviewLabel(vacancy.review_status)}
        </Badge>
      </div>
    </>
  );
}
