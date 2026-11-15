import { useState } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, ExtractionRun } from "./api";
import { getLatestExtractionRunSummary } from "./job-management/latest-extraction-run-summary";

export type VacancyRunSummary = ReturnType<typeof getLatestExtractionRunSummary>;

type Options = {
  dashboardSources: EmployerSource[];
  employers: Employer[];
  setExtracting: (value: boolean) => void;
  loadWorkspace: () => Promise<void>;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export function useVacancyFetching({
  dashboardSources, employers, setExtracting, loadWorkspace, onError, onNotice,
}: Options) {
  const [runSummary, setRunSummary] = useState<VacancyRunSummary>(null);

  async function fetchJobs() {
    if (!dashboardSources.length) {
      onError("No job sources are registered. Add an official careers URL first.");
      return;
    }
    setExtracting(true);
    setRunSummary(null);
    onError("");
    onNotice("");
    try {
      const results = await Promise.allSettled(
        dashboardSources.map((source) => scoutApi.extractSource(source.id)),
      );
      const completed = results.flatMap((result, index) =>
        result.status === "fulfilled"
          ? [{ run: result.value as ExtractionRun, source: dashboardSources[index] }]
          : [],
      ).filter(({ run }) => run.complete && ["success", "empty"].includes(run.outcome));
      const summary = getLatestExtractionRunSummary(
        completed.map(({ source }) => source),
        Object.fromEntries(completed.map(({ source, run }) => [source.id, [run]])),
        employers,
      );
      setRunSummary(summary);
      await loadWorkspace();
      const failed = results.length - completed.length;
      onNotice(failed
        ? \`Fetch finished: \${completed.length} source(s) returned; \${failed} failed.\`
        : \`Fetch finished: +\${summary?.added ?? 0} added, −\${summary?.missing ?? 0} missing, net \${summary?.net ?? 0}. Initial collections: \${summary?.baselineCount ?? 0}.\`);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not fetch jobs.");
    } finally {
      setExtracting(false);
    }
  }
  return { fetchJobs, runSummary };
}
