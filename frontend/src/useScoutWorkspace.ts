import { useCallback, useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "./api";
import type { Employer, Vacancy } from "./api";

type UseScoutWorkspaceResult = {
  employers: Employer[];
  setEmployers: Dispatch<SetStateAction<Employer[]>>;
  vacancies: Vacancy[];
  setVacancies: Dispatch<SetStateAction<Vacancy[]>>;
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
): UseScoutWorkspaceResult {
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [archivedVacancies, setArchivedVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [archivedLoading, setArchivedLoading] = useState(false);
  const [archivedLoaded, setArchivedLoaded] = useState(false);

  const loadArchivedVacancies = useCallback(async (force = false) => {
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
  }, [archivedLoaded, onError]);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    onError("");
    try {
      const [nextEmployers, nextVacancies] = await Promise.all([
        scoutApi.listEmployers(),
        scoutApi.listVacancies(),
      ]);
      setEmployers(nextEmployers);
      setVacancies(nextVacancies);
      void loadDashboardData();
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, [onError, loadDashboardData]);

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
    archivedVacancies,
    setArchivedVacancies,
    loading: loading || (showArchived && archivedLoading),
    loadWorkspace,
    loadArchivedVacancies,
  };
}
