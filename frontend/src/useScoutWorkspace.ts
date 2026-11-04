import { useCallback, useEffect, useState } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, ExtractionRun, Vacancy } from "./api";

type UseScoutWorkspaceResult = {
  employers: Employer[];
  setEmployers: React.Dispatch<React.SetStateAction<Employer[]>>;
  vacancies: Vacancy[];
  setVacancies: React.Dispatch<React.SetStateAction<Vacancy[]>>;
  archivedVacancies: Vacancy[];
  setArchivedVacancies: React.Dispatch<React.SetStateAction<Vacancy[]>>;
  dashboardSources: EmployerSource[];
  setDashboardSources: React.Dispatch<React.SetStateAction<EmployerSource[]>>;
  extractionRuns: Record<string, ExtractionRun[]>;
  setExtractionRuns: React.Dispatch<React.SetStateAction<Record<string, ExtractionRun[]>>>;
  loading: boolean;
  loadWorkspace: () => Promise<void>;
};

export function useScoutWorkspace(
  onError: (message: string) => void,
): UseScoutWorkspaceResult {
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [archivedVacancies, setArchivedVacancies] = useState<Vacancy[]>([]);
  const [dashboardSources, setDashboardSources] = useState<EmployerSource[]>([]);
  const [extractionRuns, setExtractionRuns] = useState<Record<string, ExtractionRun[]>>({});
  const [loading, setLoading] = useState(true);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    onError("");
    try {
      const [nextEmployers, nextVacancies, nextArchived] = await Promise.all([
        scoutApi.listEmployers(),
        scoutApi.listVacancies(),
        scoutApi.listArchivedVacancies(),
      ]);
      setEmployers(nextEmployers);
      setVacancies(nextVacancies);
      setArchivedVacancies(nextArchived);

      const sourceGroups = await Promise.all(
        nextEmployers.map(async (employer) => ({
          employer,
          sources: await scoutApi.listSources(employer.id),
        })),
      );
      const allSources = sourceGroups.flatMap((group) => group.sources);
      setDashboardSources(allSources);

      const runEntries = await Promise.all(
        allSources.map(
          async (source) => [source.id, await scoutApi.listExtractionRuns(source.id)] as const,
        ),
      );
      setExtractionRuns(Object.fromEntries(runEntries));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, [onError]);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  return {
    employers,
    setEmployers,
    vacancies,
    setVacancies,
    archivedVacancies,
    setArchivedVacancies,
    dashboardSources,
    setDashboardSources,
    extractionRuns,
    setExtractionRuns,
    loading,
    loadWorkspace,
  };
}
