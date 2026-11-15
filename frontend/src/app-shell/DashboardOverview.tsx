import {
  ArrowDownRight,
  ArrowUpRight,
  BriefcaseBusiness,
  Building2,
  CalendarX2,
  Clock3,
  Sparkles,
} from "lucide-react";

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

type MetricCardProps = {
  label: string;
  value: number;
  icon: typeof BriefcaseBusiness;
};

function MetricCard({ label, value, icon: Icon }: MetricCardProps) {
  return (
    <div className="scout-vacancy-count-card">
      <span className="scout-vacancy-count-card__icon">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <p className="text-xl font-bold leading-tight text-primary">{value.toLocaleString()}</p>
      </div>
    </div>
  );
}

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
    <div className="space-y-3">
      <div className="flex flex-wrap items-stretch gap-3">
        <MetricCard label="Collected vacancies" value={vacancyCount} icon={BriefcaseBusiness} />
        <MetricCard label="Registered companies" value={companyCount} icon={Building2} />
        <MetricCard label="First seen (24h)" value={newCount} icon={Sparkles} />
        <MetricCard label="Old vacancies" value={oldCount} icon={Clock3} />
        <MetricCard label="No publication date" value={undatedCount} icon={CalendarX2} />
      </div>
      {extracting ? (
        <span className="text-xs text-muted-foreground">Crawler running…</span>
      ) : (
        runSummary && (
          <div className="flex flex-wrap items-center gap-2 text-xs" aria-live="polite">
            <span className="font-semibold">Latest completed run:</span>
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
