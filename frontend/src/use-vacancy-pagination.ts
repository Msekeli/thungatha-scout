import { useCallback, useRef, useState } from "react";
import { scoutApi } from "./api";
import type { Vacancy, VacancyAgeFilter, VacancyLocationScope } from "./api";

const PAGE_SIZE = 50;

type VacancyFilters = {
  employerId: string;
  locationScope: VacancyLocationScope;
  ageFilter: VacancyAgeFilter;
};

export function useVacancyPagination(filters: VacancyFilters, onError: (message: string) => void) {
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [totalVacancies, setTotalVacancies] = useState(0);
  const [hasMoreVacancies, setHasMoreVacancies] = useState(false);
  const [loadingFirstPage, setLoadingFirstPage] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const nextOffset = useRef(0);
  const requestGeneration = useRef(0);
  const moreRequestInFlight = useRef(false);

  const loadFirstPage = useCallback(async () => {
    const generation = ++requestGeneration.current;
    nextOffset.current = 0;
    moreRequestInFlight.current = false;
    setLoadingFirstPage(true);
    setLoadingMore(false);
    setVacancies([]);
    setTotalVacancies(0);
    setHasMoreVacancies(false);

    try {
      const page = await scoutApi.listVacancies({
        ...filters,
        limit: PAGE_SIZE,
        offset: 0,
      });
      if (generation !== requestGeneration.current) return;
      setVacancies(page.items);
      setTotalVacancies(page.total);
      setHasMoreVacancies(page.has_more);
      nextOffset.current = page.offset + page.items.length;
    } catch (reason) {
      if (generation !== requestGeneration.current) return;
      onError(reason instanceof Error ? reason.message : "Could not load vacancies.");
    } finally {
      if (generation === requestGeneration.current) setLoadingFirstPage(false);
    }
  }, [filters, onError]);

  const loadMoreVacancies = useCallback(async () => {
    if (moreRequestInFlight.current || loadingFirstPage || !hasMoreVacancies) return;
    const generation = requestGeneration.current;
    moreRequestInFlight.current = true;
    setLoadingMore(true);
    try {
      const page = await scoutApi.listVacancies({
        ...filters,
        limit: PAGE_SIZE,
        offset: nextOffset.current,
      });
      if (generation !== requestGeneration.current) return;
      setVacancies((current) => [...current, ...page.items]);
      nextOffset.current = page.offset + page.items.length;
      setTotalVacancies(page.total);
      setHasMoreVacancies(page.has_more);
    } catch (reason) {
      if (generation === requestGeneration.current) {
        onError(reason instanceof Error ? reason.message : "Could not load more vacancies.");
      }
    } finally {
      if (generation === requestGeneration.current) {
        moreRequestInFlight.current = false;
        setLoadingMore(false);
      }
    }
  }, [filters, hasMoreVacancies, loadingFirstPage, onError]);

  return {
    vacancies,
    setVacancies,
    totalVacancies,
    hasMoreVacancies,
    loadingFirstPage,
    loadingMore,
    loadFirstPage,
    loadMoreVacancies,
  };
}
