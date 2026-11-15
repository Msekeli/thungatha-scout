import {
  BriefcaseBusiness,
  Building2,
  CalendarX2,
  Clock3,
  Hourglass,
  Sparkles,
  Timer,
} from "lucide-react";
import { DashboardMetricCard } from "./DashboardMetricCard";
import { DashboardRunSummary, type RunSummary } from "./DashboardRunSummary";

type Props = {
  vacancyCount: number;
  companyCount: number;
  newCount: number;
  freshCount: number;
  recentCount: number;
  agingCount: number;
  staleCount: number;
  undatedCount: number;
  runSummary: RunSummary | null;
  extracting: boolean;
};

export function DashboardOverview({
  vacancyCount,
  companyCount,
  newCount,
  freshCount,
  recentCount,
  agingCount,
  staleCount,
  undatedCount,
  runSummary,
  extracting,
}: Props) {
  return (
    <div className="min-w-0 flex-1 space-y-3">
      <div className="flex flex-wrap items-stretch gap-2">
        <DashboardMetricCard label="Collected vacancies" value={vacancyCount} icon={BriefcaseBusiness} />
        <DashboardMetricCard label="Registered companies" value={companyCount} icon={Building2} />
        <DashboardMetricCard label="First seen (24h)" value={newCount} icon={Sparkles} />
        <DashboardMetricCard label="Fresh (0–7 days)" value={freshCount} icon={Timer} />
        <DashboardMetricCard label="Recent (8–14 days)" value={recentCount} icon={Clock3} />
        <DashboardMetricCard label="Aging (15–30 days)" value={agingCount} icon={Hourglass} />
        <DashboardMetricCard label="Stale (over 30 days)" value={staleCount} icon={Clock3} />
        <DashboardMetricCard label="Date unavailable" value={undatedCount} icon={CalendarX2} />
      </div>
      <DashboardRunSummary summary={runSummary} extracting={extracting} />
    </div>
  );
}
