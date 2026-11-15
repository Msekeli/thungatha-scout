import { useCallback, useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "./api";
import type { Employer, Vacancy, VacancyAgeFilter, VacancyLocationScope } from "./api";
import type { VacancyDashboardMetrics } from "./api-services/vacancy-api-client";
import { useArchivedVacancies } from "./use-archived-vacancies";
import { useVacancyPagination } from "./use-vacancy-pagination";
import { useScoutWorkspaceReferenceData } from "./use-scout-workspace-reference-data";

type UseScoutWorkspaceResult = {
  employers: Employer[];
  setEmployers: Dispatch<SetStateAction<Employer[]>>;
  vacancies: Vacancy[];
  setVacancies: Dispatch<SetStateAction<Vacancy[]>>;
  totalVacancies: number;
  dashboardMetrics: VacancyDashboardMetrics;
  hasMoreVacancies: boolean;
  loadingFirstPage: boolean;
  loadingMore: boolean;
  loadMoreVacancies: () => Promise<void>;
  archivedVacancies: Vacancy[];
  setArchivedVacancies: Dispatch<SetStateAction<Vacancy[]>>;
  loading: boolean;
  loadWorkspace: () => Promise<void>;
  loadArchivedVacancies: (force?: boolean) => Promise<void>;
};

export function useScoutWorkspace(
  onError: (message: string) => void,
  showArchived: boolean,
  loadDashboardData: () => Promise<void>,
  filters: { employerId: string; locationScope: VacancyLocationScope; ageFilter: VacancyAgeFilter },
): UseScoutWorkspaceResult {
  const [loading, setLoading] = useState(true);
  const referenceData = useScoutWorkspaceReferenceData(onError, loadDashboardData, setLoading);
  const activeVacancies = useVacancyPagination(filters, onError);
  const archived = useArchivedVacancies(onError);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    onError("");
    try {
      const [employers, , metrics] = await Promise.all([
        scoutApi.listEmployers(),
        activeVacancies.loadFirstPage(),
        scoutApi.getVacancyMetrics(),
      ]);
      referenceData.setEmployers(employers);
      referenceData.setDashboardMetrics(metrics);
      void loadDashboardData();
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, [activeVacancies.loadFirstPage, onError, loadDashboardData, referenceData.setEmployers, referenceData.setDashboardMetrics]);

  useEffect(() => {
    void activeVacancies.loadFirstPage();
  }, [activeVacancies.loadFirstPage]);

  useEffect(() => {
    if (showArchived) void archived.loadArchivedVacancies();
  }, [showArchived, archived.loadArchivedVacancies]);

  return {
    employers: referenceData.employers,
    setEmployers: referenceData.setEmployers,
    dashboardMetrics: referenceData.dashboardMetrics,
    ...activeVacancies,
    archivedVacancies: archived.archivedVacancies,
    setArchivedVacancies: archived.setArchivedVacancies,
    loading: loading || (showArchived && archived.loading),
    loadWorkspace,
    loadArchivedVacancies: archived.loadArchivedVacancies,
  };
}
