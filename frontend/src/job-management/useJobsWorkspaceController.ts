import { useCallback, useMemo } from "react";
import { useScoutWorkspace } from "../useScoutWorkspace";
import { useScoutDashboardData } from "../useScoutDashboardData";
import { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";
import { useVacancyFetching } from "../useVacancyFetching";
import { useVacancyManagement } from "./useVacancyManagement";
import type { useScoutAppState } from "../app-state/useScoutAppState";

type AppState = ReturnType<typeof useScoutAppState>;

export function useJobsWorkspaceController(state: AppState) {
  const dashboard = useScoutDashboardData(state.setError);
  const vacancyFilters = useMemo(
    () => ({
      employerId: state.selectedEmployerId,
      locationScope: state.locationScope,
    }),
    [state.selectedEmployerId, state.locationScope],
  );
  const workspace = useScoutWorkspace(
    state.setError,
    state.showArchived,
    dashboard.loadDashboardData,
    vacancyFilters,
  );
  const loadWorkspace = useCallback(async () => {
    await workspace.loadWorkspace();
    if (state.showArchived) await workspace.loadArchivedVacancies(true);
  }, [workspace.loadWorkspace, workspace.loadArchivedVacancies, state.showArchived]);
  const management = useVacancyManagement({
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
  });
  return {
    ...workspace,
    ...dashboard,
    ...management,
    ...fetching,
    ...metrics,
    loadWorkspace,
  };
}
