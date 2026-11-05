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
  dashboardSources,
  setExtracting,
  loadWorkspace,
  onError,
  onNotice,
}: UseVacancyFetchingOptions) {
  async function fetchJobs() {
    const eligibleSources = dashboardSources.filter(
      (source) => source.status === "verified" && source.permission_status === "allowed",
    );
    if (!eligibleSources.length) {
      onError(
        "No job sources are both verified and permitted. Review company sources before fetching jobs.",
      );
      return;
    }

    setExtracting(true);
    onError("");
    onNotice("");
    try {
      const results = await Promise.allSettled(
        eligibleSources.map((source) => scoutApi.extractSource(source.id)),
      );
      const succeeded = results.filter((result) => result.status === "fulfilled").length;
      const failed = results.length - succeeded;
      await loadWorkspace();
      onNotice(
        failed
          ? `Fetched from ${succeeded} source(s); ${failed} failed. Check extraction history. Dashboard metrics are updating.`
          : `Fetch completed for ${succeeded} verified source(s). Vacancies refreshed; dashboard metrics are updating.`,
      );
    } catch (reason) {
      onError(
        reason instanceof Error ? reason.message : "Could not fetch jobs from verified sources.",
      );
    } finally {
      setExtracting(false);
    }
  }

  return { fetchJobs };
}
