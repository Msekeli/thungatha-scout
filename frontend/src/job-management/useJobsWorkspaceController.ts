import { useCallback, useMemo } from "react";
import { scoutApi } from "../api";
import { useScoutWorkspace } from "../useScoutWorkspace";
import { useScoutDashboardData } from "../useScoutDashboardData";
import { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";
import { useVacancyFetching } from "../useVacancyFetching";
import { useVacancyReview } from "./useVacancyReview";
import type { useScoutAppState } from "../app-state/useScoutAppState";

type AppState = ReturnType<typeof useScoutAppState>;

export function useJobsWorkspaceController(state: AppState) {
  const dashboard = useScoutDashboardData(state.setError);
  const vacancyFilters = useMemo(
    () => ({
      employerId: state.selectedEmployerId,
      reviewStatus: state.reviewFilter,
      locationScope: state.locationScope,
    }),
    [state.selectedEmployerId, state.reviewFilter, state.locationScope],
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
  const review = useVacancyReview({
    onVacancyUpdated: (updated) =>
      workspace.setVacancies((items) =>
        items.map((item) => (item.id === updated.id ? updated : item)),
      ),
    onRefresh: loadWorkspace,
    onNotice: state.setNotice,
    onError: state.setError,
  });
  const excludeVacancy = useCallback(
    async (vacancyId: string) => {
      try {
        const updated = await scoutApi.updateVacancyReview(
          vacancyId,
          "rejected",
          "Excluded by administrator from Thungatha publication.",
        );
        workspace.setVacancies((items) =>
          items.map((item) => (item.id === updated.id ? updated : item)),
        );
        state.setNotice("Vacancy excluded. It will not be published to Thungatha.");
      } catch (reason) {
        state.setError(reason instanceof Error ? reason.message : "Could not exclude vacancy.");
      }
    },
    [workspace.setVacancies, state.setNotice, state.setError],
  );
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
  return {
    ...workspace,
    ...dashboard,
    ...review,
    ...fetching,
    ...metrics,
    loadWorkspace,
    excludeVacancy,
  };
}
