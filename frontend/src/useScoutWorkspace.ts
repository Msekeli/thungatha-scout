import { useCallback, useEffect, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "./api";
import type { Employer, Vacancy, VacancyLocationScope, VacancyReviewStatus } from "./api";
import type { VacancyDashboardMetrics } from "./api-services/vacancy-api-client";

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

const PAGE_SIZE = 50;

export function useScoutWorkspace(
  onError: (message: string) => void,
  showArchived: boolean,
  loadDashboardData: () => Promise<void>,
  filters: {
    employerId: string;
    reviewStatus: string;
    locationScope: VacancyLocationScope;
  },
): UseScoutWorkspaceResult {
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [totalVacancies, setTotalVacancies] = useState(0);
  const [dashboardMetrics, setDashboardMetrics] = useState<VacancyDashboardMetrics>({ total_active: 0, new_last_24_hours: 0 });
  const [hasMoreVacancies, setHasMoreVacancies] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [archivedVacancies, setArchivedVacancies] = useState<Vacancy[]>([]);
  const [archivedLoading, setArchivedLoading] = useState(false);
  const [archivedLoaded, setArchivedLoaded] = useState(false);
  const nextOffset = useRef(0);
  const requestInFlight = useRef(false);

  const loadMoreVacancies = useCallback(async () => {
    if (requestInFlight.current || !hasMoreVacancies) return;
    requestInFlight.current = true;
    setLoadingMore(true);
    try {
      const page = await scoutApi.listVacancies({
        employerId: filters.employerId,
        reviewStatus: filters.reviewStatus as VacancyReviewStatus | "all",
        locationScope: filters.locationScope,
        limit: PAGE_SIZE,
        offset: nextOffset.current,
      });
      setVacancies((current) => [...current, ...page.items]);
      nextOffset.current = page.offset + page.items.length;
      setTotalVacancies(page.total);
      setHasMoreVacancies(page.has_more);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load more vacancies.");
    } finally {
      requestInFlight.current = false;
      setLoadingMore(false);
    }
  }, [filters, hasMoreVacancies, onError]);

  const loadArchivedVacancies = useCallback(
    async (force = false) => {
      if (archivedLoaded && !force) return;
      setArchivedLoading(true);
      try {
        setArchivedVacancies(await scoutApi.listArchivedVacancies());
        setArchivedLoaded(true);
      } catch (reason) {
        onError(reason instanceof Error ? reason.message : "Could not load archived vacancies.");
      } finally {
        setArchivedLoading(false);
      }
    },
    [archivedLoaded, onError],
  );

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    onError("");
    nextOffset.current = 0;
    try {
      const [nextEmployers, page, metrics] = await Promise.all([
        scoutApi.listEmployers(),
        scoutApi.listVacancies({
          employerId: filters.employerId,
          reviewStatus: filters.reviewStatus as VacancyReviewStatus | "all",
          locationScope: filters.locationScope,
          limit: PAGE_SIZE,
          offset: 0,
        }),
        scoutApi.getVacancyMetrics(),
      ]);
      setEmployers(nextEmployers);
      setDashboardMetrics(metrics);
      setVacancies(page.items);
      setTotalVacancies(page.total);
      nextOffset.current = page.items.length;
      setHasMoreVacancies(page.has_more);
      void loadDashboardData();
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, [filters, onError, loadDashboardData]);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);
  useEffect(() => {
    if (showArchived) void loadArchivedVacancies();
  }, [showArchived, loadArchivedVacancies]);

  return {
    employers,
    setEmployers,
    vacancies,
    setVacancies,
    totalVacancies,
    dashboardMetrics,
    hasMoreVacancies,
    loadingMore,
    loadMoreVacancies,
    archivedVacancies,
    setArchivedVacancies,
    loading: loading || (showArchived && archivedLoading),
    loadWorkspace,
    loadArchivedVacancies,
  };
}
