import { useCallback, useRef } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer, EmployerSource, ExtractionRun, GreenhouseInspection } from "../api";

type UseCompanySelectionOptions = {
  setSources: Dispatch<SetStateAction<EmployerSource[]>>;
  setExtractionRuns: Dispatch<SetStateAction<Record<string, ExtractionRun[]>>>;
  setSelectedEmployerId: (id: string) => void;
  setLogoUrl: (url: string) => void;
  setLogoSourceUrl: (url: string) => void;
  setSourceUrl: (url: string) => void;
  setEditingSourceId: (id: string | null) => void;
  setInspection: (inspection: GreenhouseInspection | null) => void;
  setPage: (page: "companies") => void;
  onError: (message: string) => void;
};

export function useCompanySelection({
  setSources,
  setExtractionRuns,
  setSelectedEmployerId,
  setLogoUrl,
  setLogoSourceUrl,
  setSourceUrl,
  setEditingSourceId,
  setInspection,
  setPage,
  onError,
}: UseCompanySelectionOptions) {
  const requestId = useRef(0);

  const openCompany = useCallback(async (employer: Employer) => {
    const currentRequest = ++requestId.current;
    setEditingSourceId(null);
    setSourceUrl("");
    setInspection(null);
    setSelectedEmployerId(employer.id);
    setLogoUrl(employer.logo_url ?? "");
    setLogoSourceUrl(employer.logo_source_url ?? "");
    setPage("companies");
    onError("");

    try {
      const nextSources = await scoutApi.listSources(employer.id);
      const runEntries = await Promise.all(
        nextSources.map(
          async (source) => [source.id, await scoutApi.listExtractionRuns(source.id)] as const,
        ),
      );

      if (currentRequest !== requestId.current) return;

      setSources(nextSources);
      setExtractionRuns((current) => ({
        ...current,
        ...Object.fromEntries(runEntries),
      }));
    } catch (reason) {
      if (currentRequest !== requestId.current) return;
      onError(reason instanceof Error ? reason.message : "Could not load company sources.");
    }
  }, [
    onError,
    setEditingSourceId,
    setExtractionRuns,
    setInspection,
    setLogoSourceUrl,
    setLogoUrl,
    setPage,
    setSelectedEmployerId,
    setSourceUrl,
    setSources,
  ]);

  return { openCompany };
}
