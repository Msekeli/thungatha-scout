import { useCallback, useRef, useState } from "react";
import { scoutApi } from "./api";
import type { Vacancy, VacancyLocationScope } from "./api";

const PAGE_SIZE = 50;

type VacancyFilters = {
  employerId: string;
  locationScope: VacancyLocationScope;
};

export function useVacancyPagination(
  filters: VacancyFilters,
  onError: (message: string) => void,
) {
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [totalVacancies, setTotalVacancies] = useState(0);
  const [hasMoreVacancies, setHasMoreVacancies] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const nextOffset = useRef(0);
  const requestInFlight = useRef(false);

  const loadFirstPage = useCallback(async () => {
    nextOffset.current = 0;
    const page = await scoutApi.listVacancies({
      ...filters,
      limit: PAGE_SIZE,
      offset: 0,
    });
    setVacancies(page.items);
    setTotalVacancies(page.total);
    setHasMoreVacancies(page.has_more);
    nextOffset.current = page.offset + page.items.length;
  }, [filters]);

  const loadMoreVacancies = useCallback(async () => {
    if (requestInFlight.current || !hasMoreVacancies) return;
    requestInFlight.current = true;
    setLoadingMore(true);
    try {
      const page = await scoutApi.listVacancies({
        ...filters,
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

  return {
    vacancies,
    setVacancies,
    totalVacancies,
    hasMoreVacancies,
    loadingMore,
    loadFirstPage,
    loadMoreVacancies,
  };
}
