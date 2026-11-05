import { ArrowDownRight, ArrowUpRight, BriefcaseBusiness } from "lucide-react";

type Props = {
  vacancyCount: number;
  vacancyChange: number;
};

export function DashboardOverview({ vacancyCount, vacancyChange }: Props) {
  return (
    <div className="scout-vacancy-count-card">
      <span className="scout-vacancy-count-card__icon">
        <BriefcaseBusiness className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-medium text-muted-foreground">Collected vacancies</p>
        <p className="text-xl font-bold leading-tight text-primary">{vacancyCount}</p>
      </div>
      {vacancyChange !== 0 && (
        <span
          className={
            "ml-auto inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold " +
            (vacancyChange > 0
              ? "scout-vacancy-change--positive"
              : "scout-vacancy-change--negative")
          }
          aria-label={
            vacancyChange > 0
              ? vacancyChange + " new vacancies in the last 24 hours"
              : Math.abs(vacancyChange) + " vacancies removed from active inventory"
          }
        >
          {vacancyChange > 0 ? (
            <ArrowUpRight className="h-3.5 w-3.5" />
          ) : (
            <ArrowDownRight className="h-3.5 w-3.5" />
          )}
          {vacancyChange > 0 ? "+" : ""}
          {vacancyChange}
        </span>
      )}
    </div>
  );
}
