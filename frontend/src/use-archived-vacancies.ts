import { useCallback, useState } from "react";
import { scoutApi } from "./api";
import type { Vacancy } from "./api";

export function useArchivedVacancies(onError: (message: string) => void) {
  const [archivedVacancies, setArchivedVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const loadArchivedVacancies = useCallback(
    async (force = false) => {
      if (loaded && !force) return;
      setLoading(true);
      try {
        setArchivedVacancies(await scoutApi.listArchivedVacancies());
        setLoaded(true);
      } catch (reason) {
        onError(reason instanceof Error ? reason.message : "Could not load archived vacancies.");
      } finally {
        setLoading(false);
      }
    },
    [loaded, onError],
  );

  return {
    archivedVacancies,
    setArchivedVacancies,
    loading,
    loadArchivedVacancies,
  };
}
