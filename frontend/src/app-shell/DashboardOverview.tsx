import { ArrowDownRight, ArrowUpRight, BriefcaseBusiness } from "lucide-react";

type RunSummary = {
  added: number;
  missing: number;
  net: number;
  companies: { name: string; added: number; missing: number; baseline: boolean }[];
  baselineCount: number;
};

type Props = {
  vacancyCount: number;
  companyCount: number;
  newCount: number;
  oldCount: number;
  undatedCount: number;
  runSummary: RunSummary | null;
  extracting: boolean;
};

export function DashboardOverview({
  vacancyCount,
  companyCount,
  newCount,
  oldCount,
  undatedCount,
  runSummary,
  extracting,
}: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="scout-vacancy-count-card">
        <BriefcaseBusiness className="h-5 w-5" aria-hidden="true" />
        <div>
          <p className="text-xs text-muted-foreground">Collected vacancies</p>
          <p className="text-xl font-bold text-primary">{vacancyCount.toLocaleString()}</p>
        </div>
      </div>
      <span className="rounded-md bg-muted px-2 py-1 text-xs">Companies: {companyCount}</span>
      <div className="flex flex-wrap gap-2 text-xs">
        <span className="rounded-md bg-muted px-2 py-1">New: {newCount}</span>
        <span className="rounded-md bg-muted px-2 py-1">Old: {oldCount}</span>
        <span className="rounded-md bg-muted px-2 py-1">No date: {undatedCount}</span>
      </div>
      {extracting ? (
        <span className="text-xs text-muted-foreground">Crawler running…</span>
      ) : (
        runSummary && (
          <div className="flex flex-wrap items-center gap-2 text-xs" aria-live="polite">
            <span className="font-semibold">Latest run:</span>
            <span className="inline-flex items-center gap-1 text-muted-foreground">
              <ArrowUpRight className="h-3 w-3" /> +{runSummary.added} added
            </span>
            <span className="inline-flex items-center gap-1 text-muted-foreground">
              <ArrowDownRight className="h-3 w-3" /> −{runSummary.missing} missing
            </span>
            <span className="text-muted-foreground">
              Net {runSummary.net >= 0 ? "+" : ""}
              {runSummary.net}
            </span>
            {runSummary.baselineCount > 0 && (
              <span className="text-muted-foreground">
                Initial collection:{" "}
                {runSummary.companies
                  .filter((item) => item.baseline)
                  .map((item) => item.name)
                  .join(", ")}
              </span>
            )}
            {runSummary.companies
              .filter((item) => item.added || item.missing)
              .map((item) => (
                <span key={item.name} className="text-muted-foreground">
                  {item.name}: +{item.added}/−{item.missing}
                </span>
              ))}
          </div>
        )
      )}
    </div>
  );
}
