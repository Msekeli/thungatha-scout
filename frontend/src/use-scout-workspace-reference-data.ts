import { useEffect, useState } from "react";
import { scoutApi } from "./api";
import type { Employer } from "./api";
import type { VacancyDashboardMetrics } from "./api-services/vacancy-api-client";

const EMPTY_METRICS: VacancyDashboardMetrics = {
  total_active: 0,
  new_last_24_hours: 0,
  fresh_vacancies: 0,
  recent_vacancies: 0,
  aging_vacancies: 0,
  stale_vacancies: 0,
  undated_vacancies: 0,
};

export function useScoutWorkspaceReferenceData(
  onError: (message: string) => void,
  loadDashboardData: () => Promise<void>,
  setLoading: (loading: boolean) => void,
) {
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [dashboardMetrics, setDashboardMetrics] = useState(EMPTY_METRICS);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    onError("");
    Promise.all([scoutApi.listEmployers(), scoutApi.getVacancyMetrics()])
      .then(([nextEmployers, metrics]) => {
        if (cancelled) return;
        setEmployers(nextEmployers);
        setDashboardMetrics(metrics);
        void loadDashboardData();
      })
      .catch(
        (reason: unknown) =>
          !cancelled &&
          onError(reason instanceof Error ? reason.message : "Could not load Scout data."),
      )
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [onError, loadDashboardData, setLoading]);

  return { employers, setEmployers, dashboardMetrics, setDashboardMetrics };
}
