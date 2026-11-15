import { useCallback, useState } from "react";
import { scoutApi } from "./api";
import type { EmployerSource, ExtractionRun } from "./api";

export function useScoutDashboardData(onError: (message: string) => void) {
  const [dashboardSources, setDashboardSources] = useState<EmployerSource[]>([]);
  const [extractionRuns, setExtractionRuns] = useState<Record<string, ExtractionRun[]>>({});

  const loadDashboardData = useCallback(async () => {
    try {
      const [sources, runs] = await Promise.all([
        scoutApi.listAllSources(),
        scoutApi.listAllExtractionRuns(),
      ]);
      const groupedRuns = runs.reduce<Record<string, ExtractionRun[]>>((groups, run) => {
        (groups[run.source_id] ??= []).push(run);
        return groups;
      }, {});
      setDashboardSources(sources);
      setExtractionRuns(groupedRuns);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not load dashboard history.");
    }
  }, [onError]);

  return {
    dashboardSources,
    setDashboardSources,
    extractionRuns,
    setExtractionRuns,
    loadDashboardData,
  };
}
