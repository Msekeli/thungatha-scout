import { useMemo } from "react";
import type { Employer, EmployerSource, ExtractionRun, Vacancy } from "./api";

type UseScoutDashboardMetricsOptions = {
  employers: Employer[];
  vacancies: Vacancy[];
  archivedVacancies: Vacancy[];
  dashboardSources: EmployerSource[];
  extractionRuns: Record<string, ExtractionRun[]>;
  showArchived: boolean;
  selectedEmployerId: string;
  reviewFilter: string;
};

export function useScoutDashboardMetrics({
  employers, vacancies, archivedVacancies, dashboardSources, extractionRuns,
  showArchived, selectedEmployerId, reviewFilter,
}: UseScoutDashboardMetricsOptions) {
  const newVacancies24h = vacancies.filter(
    (item) => item.first_seen_at && Date.now() - new Date(item.first_seen_at).getTime() < 86400000,
  ).length;
  const attentionCount = vacancies.filter(
    (item) => item.review_status === "pending" || item.review_status === "needs_verification",
  ).length;

  const atsPerformance = useMemo(
    () => Array.from(new Set(["greenhouse", ...dashboardSources.map((source) => source.adapter_key)]))
      .map((adapter) => {
        const adapterSources = dashboardSources.filter((source) => source.adapter_key === adapter);
        const runs = adapterSources.flatMap((source) => extractionRuns[source.id] ?? []);
        const latest = [...runs].sort(
          (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
        )[0];
        return {
          adapter,
          sourceCount: adapterSources.length,
          verified: adapterSources.filter(
            (source) => source.status === "verified" && source.permission_status === "allowed",
          ).length,
          jobCount: vacancies.filter((job) => adapterSources.some((source) => source.id === job.source_id)).length,
          latest,
          failed: runs.filter((run) => !["success", "empty"].includes(run.outcome)).length,
        };
      }),
    [dashboardSources, extractionRuns, vacancies],
  );

  const visibleVacancies = showArchived ? archivedVacancies : vacancies;
  const filteredVacancies = useMemo(
    () => visibleVacancies
      .filter((item) => selectedEmployerId === "all" || item.employer_id === selectedEmployerId)
      .filter((item) => reviewFilter === "all" || item.review_status === reviewFilter),
    [visibleVacancies, selectedEmployerId, reviewFilter],
  );

  return {
    newVacancies24h, attentionCount, atsPerformance, visibleVacancies,
    filteredVacancies, employerCount: employers.length,
  };
}
