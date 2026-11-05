import { Button } from "@/components/ui/button";
import { CalendarDays, Building2, MapPin } from "lucide-react";
import type { Vacancy } from "../api";

export function VacancyDetailsHeader({ vacancy }: { vacancy: Vacancy }) {
  const postedAt = vacancy.first_seen_at ?? vacancy.last_seen_at;
  return (
    <>
      <div className="space-y-3 border-b border-border bg-card p-4 text-card-foreground">
        <div>
          <p className="text-xs font-semibold text-scout-cyan">Company</p>
          <p className="mt-0.5 text-sm font-semibold">{vacancy.employer_name}</p>
        </div>
        <div className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-scout-cyan" />
            {vacancy.location_text || "Location unknown"}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <CalendarDays className="h-3.5 w-3.5 text-scout-cyan" />
            {new Date(postedAt).toLocaleDateString()}
          </span>
        </div>
        <div className="border-t border-border pt-3">
          <p className="text-xs font-semibold text-muted-foreground">Position</p>
          <h3 className="mt-1 text-base font-bold text-foreground">{vacancy.title}</h3>
        </div>
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
