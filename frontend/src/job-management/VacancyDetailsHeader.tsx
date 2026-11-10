import { Button } from "@/components/ui/button";
import { CalendarDays, MapPin } from "lucide-react";
import type { Vacancy } from "../api";
import { getVacancyFreshness } from "./vacancy-freshness";

export function VacancyDetailsHeader({ vacancy }: { vacancy: Vacancy }) {
  const freshness = getVacancyFreshness(vacancy.source_updated_at, vacancy.published_at);
  return (
    <>
      <div className="flex flex-wrap items-center gap-x-8 gap-y-4 border-b border-border bg-card p-4 text-card-foreground">
        <div className="min-w-[120px]">
          <p className="text-xs font-semibold text-scout-cyan">Company</p>
          <p className="mt-0.5 text-sm font-semibold">{vacancy.employer_name}</p>
        </div>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-scout-cyan" />
            {vacancy.location_text || "Location unknown"}
          </span>
          <span className={`scout-vacancy-date ${freshness ? `scout-vacancy-date--${freshness.tone}` : ""}`}>
            <CalendarDays className="h-3.5 w-3.5" />
            {freshness?.label ?? "Date unavailable"}
          </span>
        </div>
        <div className="min-w-[260px] flex-1 border-l border-border pl-6">
          <p className="text-xs font-semibold text-muted-foreground">Position</p>
          <h3 className="mt-0.5 text-base font-bold leading-snug text-foreground">
            {vacancy.title}
          </h3>
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
