type Props = {
  vacancyCount: number;
  vacancyChange: number;
};

export function DashboardOverview({ vacancyCount, vacancyChange }: Props) {
  return (
    <div className="flex min-w-0 items-center gap-3">
      <div className="min-w-0">
        <p className="text-xs font-medium text-muted-foreground">Collected vacancies</p>
        <p className="text-xl font-bold leading-tight text-primary">{vacancyCount}</p>
      </div>
      {vacancyChange !== 0 && (
        <span
          className={
            "inline-flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold " +
            (vacancyChange > 0
              ? "scout-vacancy-change--positive"
              : "scout-vacancy-change--negative")
          }
          aria-label={
            vacancyChange > 0
              ? vacancyChange + " more vacancies since last visit"
              : Math.abs(vacancyChange) + " fewer vacancies since last visit"
          }
        >
          {vacancyChange > 0 ? "+" : ""}
          {vacancyChange}
        </span>
      )}
    </div>
  );
}
