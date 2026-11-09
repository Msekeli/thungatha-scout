import { useMemo } from "react";
import type { Employer, EmployerSource, ExtractionRun, Vacancy } from "./api";

type Options = {
  employers: Employer[];
  vacancies: Vacancy[];
  archivedVacancies: Vacancy[];
  dashboardSources: EmployerSource[];
  extractionRuns: Record<string, ExtractionRun[]>;
  showArchived: boolean;
  selectedEmployerId: string;
};

export function useScoutDashboardMetrics({
  employers, vacancies, archivedVacancies, dashboardSources, extractionRuns,
  showArchived, selectedEmployerId,
}: Options) {
  const newVacancies24h = vacancies.filter(
    (item) => item.first_seen_at && Date.now() - new Date(item.first_seen_at).getTime() < 86400000,
  ).length;
  const atsPerformance = useMemo(() =>
    Array.from(new Set(["greenhouse", ...dashboardSources.map((source) => source.adapter_key)]))
      .map((adapter) => {
        const sources = dashboardSources.filter((source) => source.adapter_key === adapter);
        const runs = sources.flatMap((source) => extractionRuns[source.id] ?? []);
        const latest = [...runs].sort(
          (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
        )[0];
        return {
          adapter, sourceCount: sources.length,
          jobCount: vacancies.filter((job) => sources.some((source) => source.id === job.source_id)).length,
          latest, failed: runs.filter((run) => !["success", "empty"].includes(run.outcome)).length,
        };
      }), [dashboardSources, extractionRuns, vacancies]);
  const visibleVacancies = showArchived ? archivedVacancies : vacancies;
  const filteredVacancies = useMemo(() => visibleVacancies.filter(
    (item) => selectedEmployerId === "all" || item.employer_id === selectedEmployerId,
  ), [visibleVacancies, selectedEmployerId]);
  return {
    newVacancies24h, atsPerformance, visibleVacancies, filteredVacancies,
    employerCount: employers.length,
  };
}
