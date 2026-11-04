import { useScoutWorkspace } from "../useScoutWorkspace";
import { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";
import { useVacancyFetching } from "../useVacancyFetching";
import { useVacancyReview } from "./useVacancyReview";
import type { useScoutAppState } from "../app-state/useScoutAppState";

type AppState = ReturnType<typeof useScoutAppState>;

export function useJobsWorkspaceController(state: AppState) {
  const workspace = useScoutWorkspace(state.setError);
  const review = useVacancyReview({
    onVacancyUpdated: (updated) => workspace.setVacancies((items) =>
      items.map((item) => item.id === updated.id ? updated : item)),
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

  return { ...workspace, ...review, ...fetching, ...metrics };
}
