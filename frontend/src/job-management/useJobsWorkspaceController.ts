import { useCallback } from "react";
import { useScoutWorkspace } from "../useScoutWorkspace";
import { useScoutDashboardData } from "../useScoutDashboardData";
import { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";
import { useVacancyFetching } from "../useVacancyFetching";
import { useVacancyReview } from "./useVacancyReview";
import type { useScoutAppState } from "../app-state/useScoutAppState";

type AppState = ReturnType<typeof useScoutAppState>;

export function useJobsWorkspaceController(state: AppState) {
  const dashboard = useScoutDashboardData(state.setError);
  const workspace = useScoutWorkspace(
    state.setError,
    state.showArchived,
    dashboard.loadDashboardData,
  );
  const loadWorkspace = useCallback(async () => {
    await workspace.loadWorkspace();
    if (state.showArchived) await workspace.loadArchivedVacancies(true);
  }, [workspace.loadWorkspace, workspace.loadArchivedVacancies, state.showArchived]);
  const review = useVacancyReview({
    onVacancyUpdated: (updated) =>
      workspace.setVacancies((items) =>
        items.map((item) => (item.id === updated.id ? updated : item)),
      ),
    onRefresh: loadWorkspace,
    onNotice: state.setNotice,
    onError: state.setError,
  });
  const fetching = useVacancyFetching({
    dashboardSources: dashboard.dashboardSources,
    setExtracting: state.setExtracting,
    loadWorkspace,
    onError: state.setError,
    onNotice: state.setNotice,
  });
  const metrics = useScoutDashboardMetrics({
    employers: workspace.employers,
    vacancies: workspace.vacancies,
    archivedVacancies: workspace.archivedVacancies,
    dashboardSources: dashboard.dashboardSources,
    extractionRuns: dashboard.extractionRuns,
    showArchived: state.showArchived,
    selectedEmployerId: state.selectedEmployerId,
    reviewFilter: state.reviewFilter,
  });

  return { ...workspace, ...dashboard, ...review, ...fetching, ...metrics, loadWorkspace };
}
