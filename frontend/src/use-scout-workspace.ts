import { useCallback, useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "./api";
import type { Employer, Vacancy, VacancyLocationScope } from "./api";
import type { VacancyDashboardMetrics } from "./api-services/vacancy-api-client";
import { useArchivedVacancies } from "./use-archived-vacancies";
import { useVacancyPagination } from "./use-vacancy-pagination";

type UseScoutWorkspaceResult = {
  employers: Employer[];
  setEmployers: Dispatch<SetStateAction<Employer[]>>;
  vacancies: Vacancy[];
  setVacancies: Dispatch<SetStateAction<Vacancy[]>>;
  totalVacancies: number;
  dashboardMetrics: VacancyDashboardMetrics;
  hasMoreVacancies: boolean;
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
  filters: { employerId: string; locationScope: VacancyLocationScope },
): UseScoutWorkspaceResult {
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [dashboardMetrics, setDashboardMetrics] = useState<VacancyDashboardMetrics>({
    total_active: 0,
    new_last_24_hours: 0,
  });
  const [loading, setLoading] = useState(true);
  const activeVacancies = useVacancyPagination(filters, onError);
  const archived = useArchivedVacancies(onError);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    onError("");
    try {
      const [nextEmployers, , metrics] = await Promise.all([
        scoutApi.listEmployers(),
        activeVacancies.loadFirstPage(),
        scoutApi.getVacancyMetrics(),
      ]);
      setEmployers(nextEmployers);
      setDashboardMetrics(metrics);
      void loadDashboardData();
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, [activeVacancies.loadFirstPage, onError, loadDashboardData]);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);
  useEffect(() => {
    if (showArchived) void archived.loadArchivedVacancies();
  }, [showArchived, archived.loadArchivedVacancies]);

  return {
    employers,
    setEmployers,
    ...activeVacancies,
    archivedVacancies: archived.archivedVacancies,
    setArchivedVacancies: archived.setArchivedVacancies,
    loading: loading || (showArchived && archived.loading),
    loadWorkspace,
    loadArchivedVacancies: archived.loadArchivedVacancies,
  };
}
