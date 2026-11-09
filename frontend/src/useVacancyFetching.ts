import { scoutApi } from "./api";
import type { EmployerSource } from "./api";

type UseVacancyFetchingOptions = {
  dashboardSources: EmployerSource[];
  setExtracting: (value: boolean) => void;
  loadWorkspace: () => Promise<void>;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export function useVacancyFetching({
  dashboardSources, setExtracting, loadWorkspace, onError, onNotice,
}: UseVacancyFetchingOptions) {
  async function fetchJobs() {
    if (!dashboardSources.length) {
      onError("No job sources are registered. Add a Greenhouse or Lever careers URL first.");
      return;
    }
    setExtracting(true);
    onError("");
    onNotice("");
    try {
      const results = await Promise.allSettled(
        dashboardSources.map((source) => scoutApi.extractSource(source.id)),
      );
      const succeeded = results.filter((result) => result.status === "fulfilled").length;
      const failed = results.length - succeeded;
      await loadWorkspace();
      onNotice(failed
        ? `Fetched from ${succeeded} source(s); ${failed} failed. Check extraction history.`
        : `Fetch completed for ${succeeded} source(s). Vacancies refreshed.`);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not fetch jobs.");
    } finally {
      setExtracting(false);
    }
  }
  return { fetchJobs };
}
