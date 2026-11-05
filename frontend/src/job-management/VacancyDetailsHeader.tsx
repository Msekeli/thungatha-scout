import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";

export function VacancyDetailsHeader({ vacancy }: { vacancy: Vacancy }) {
  return (
    <>
      <div className="border-b border-border bg-card p-4 text-card-foreground">
        <p className="text-[10px] font-medium text-scout-cyan">
          {vacancy.employer_name} · {vacancy.location_text || "Location unknown"}
        </p>
        <h3 className="mt-1 text-sm font-bold">{vacancy.title}</h3>
      </div>
      <div className="border-b border-border px-4 py-3">
        <Button asChild size="sm" variant="outline">
          <a href={vacancy.source_url} target="_blank" rel="noreferrer">
            Source record ↗
          </a>
        </Button>
      </div>
    </>
  );
}
