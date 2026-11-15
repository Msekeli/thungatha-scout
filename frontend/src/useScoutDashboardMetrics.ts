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
  employers,
  vacancies,
  archivedVacancies,
  dashboardSources,
  extractionRuns,
  showArchived,
  selectedEmployerId,
}: Options) {
  const newVacancies24h = vacancies.filter(
    (item) => item.first_seen_at && Date.now() - new Date(item.first_seen_at).getTime() < 86400000,
  ).length;
  const atsPerformance = useMemo(
    () =>
      Array.from(
        new Set(["greenhouse", ...dashboardSources.map((source) => source.adapter_key)]),
      ).map((adapter) => {
        const sources = dashboardSources.filter((source) => source.adapter_key === adapter);
        const runs = sources.flatMap((source) => extractionRuns[source.id] ?? []);
        const latest = [...runs].sort(
          (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
        )[0];
        return {
          adapter,
          sourceCount: sources.length,
          jobCount: vacancies.filter((job) => sources.some((source) => source.id === job.source_id))
            .length,
          latest,
          failed: runs.filter((run) => !["success", "empty"].includes(run.outcome)).length,
        };
      }),
    [dashboardSources, extractionRuns, vacancies],
  );

  const latestRunSummary = useMemo(() => {
    const latest = dashboardSources.flatMap((source) => {
      const run = extractionRuns[source.id]?.[0];
      return run?.complete && ["success", "empty"].includes(run.outcome) ? [{ source, run }] : [];
    });
    if (!latest.length) return null;
    const companies = new Map<
      string,
      {
        name: string;
        added: number;
        missing: number;
        baseline: boolean;
      }
    >();
    latest.forEach(({ source, run }) => {
      const name =
        employers.find((item) => item.id === source.employer_id)?.name ?? "Unknown company";
      const item = companies.get(source.employer_id) ?? {
        name,
        added: 0,
        missing: 0,
        baseline: false,
      };
      item.added += run.jobs_added ?? 0;
      item.missing += run.jobs_missing ?? 0;
      item.baseline ||= Boolean(run.is_baseline);
      companies.set(source.employer_id, item);
    });
    const added = latest.reduce((sum, item) => sum + (item.run.jobs_added ?? 0), 0);
    const missing = latest.reduce((sum, item) => sum + (item.run.jobs_missing ?? 0), 0);
    return {
      added,
      missing,
      net: added - missing,
      baselineCount: latest.filter((item) => item.run.is_baseline).length,
      companies: Array.from(companies.values()),
    };
  }, [dashboardSources, extractionRuns, employers]);

  const visibleVacancies = showArchived ? archivedVacancies : vacancies;
  const filteredVacancies = useMemo(
    () =>
      visibleVacancies.filter(
        (item) => selectedEmployerId === "all" || item.employer_id === selectedEmployerId,
      ),
    [visibleVacancies, selectedEmployerId],
  );
  return {
    newVacancies24h,
    latestRunSummary,
    atsPerformance,
    visibleVacancies,
    filteredVacancies,
    employerCount: employers.length,
  };
}
