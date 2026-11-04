import { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";
import { useVacancyFetching } from "../useVacancyFetching";
import { useVacancyReview } from "./useVacancyReview";
import type { useScoutWorkspace } from "../useScoutWorkspace";
import type { useScoutAppState } from "../app-shell/useScoutAppState";

type Options = {
  state: ReturnType<typeof useScoutAppState>;
  workspace: ReturnType<typeof useScoutWorkspace>;
};

export function useJobsWorkspaceController({ state, workspace }: Options) {
  const review = useVacancyReview({
    onVacancyUpdated: (updated) =>
      workspace.setVacancies((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      ),
    onRefresh: workspace.loadWorkspace,
    onNotice: state.setNotice,
    onError: state.setError,
  });

  const fetching = useVacancyFetching({
    dashboardSources: workspace.dashboardSources,
    setExtracting: state.setExtracting,
    loadWorkspace: workspace.loadWorkspace,
    onError: state.setError,
    onNotice: state.setNotice,
  });

  const metrics = useScoutDashboardMetrics({
    employers: workspace.employers,
    vacancies: workspace.vacancies,
    archivedVacancies: workspace.archivedVacancies,
    dashboardSources: workspace.dashboardSources,
    extractionRuns: workspace.extractionRuns,
    showArchived: state.showArchived,
    selectedEmployerId: state.selectedEmployerId,
    reviewFilter: state.reviewFilter,
  });

  return { review, fetchJobs: fetching.fetchJobs, metrics };
}
