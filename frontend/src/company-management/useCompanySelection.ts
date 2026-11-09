import { useCallback, useRef } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer, EmployerSource, ExtractionRun } from "../api";

type UseCompanySelectionOptions = {
  setSources: Dispatch<SetStateAction<EmployerSource[]>>;
  setDashboardSources: Dispatch<SetStateAction<EmployerSource[]>>;
  setExtractionRuns: Dispatch<SetStateAction<Record<string, ExtractionRun[]>>>;
  setSelectedCompanyId: (id: string | null) => void;
  setLogoUrl: (url: string) => void;
  setLogoSourceUrl: (url: string) => void;
  setSourceUrl: (url: string) => void;
  setEditingSourceId: (id: string | null) => void;
  setPage: (page: "companies") => void;
  onError: (message: string) => void;
};

export function useCompanySelection({
  setSources,
  setDashboardSources,
  setExtractionRuns,
  setSelectedCompanyId,
  setLogoUrl,
  setLogoSourceUrl,
  setSourceUrl,
  setEditingSourceId,
  setPage,
  onError,
}: UseCompanySelectionOptions) {
  const requestId = useRef(0);

  const openCompany = useCallback(
    async (employer: Employer) => {
      const currentRequest = ++requestId.current;
      setEditingSourceId(null);
      setSourceUrl("");
      setSources([]);
      setSelectedCompanyId(employer.id);
      setLogoUrl(employer.logo_url ?? "");
      setLogoSourceUrl(employer.logo_source_url ?? "");
      setPage("companies");
      onError("");

      try {
        const nextSources = await scoutApi.listSources(employer.id);
        const previewedSources = await Promise.all(
          nextSources.map(async (source) => {
            if (source.discovery_preview) return source;
            try {
              const preview = await scoutApi.previewSource(source.id);
              if (!preview.complete || !["success", "empty"].includes(preview.outcome))
                return source;
              return { ...source, discovery_preview: preview.discovery_preview };
            } catch {
              return source;
            }
          }),
        );
        const runEntries = await Promise.all(
          nextSources.map(
            async (source) => [source.id, await scoutApi.listExtractionRuns(source.id)] as const,
          ),
        );

        if (currentRequest !== requestId.current) return;

        setSources(previewedSources);
        setDashboardSources((current) =>
          current.map((source) => previewedSources.find((item) => item.id === source.id) ?? source),
        );
        setExtractionRuns((current) => ({
          ...current,
          ...Object.fromEntries(runEntries),
        }));
      } catch (reason) {
        if (currentRequest !== requestId.current) return;
        onError(reason instanceof Error ? reason.message : "Could not load company sources.");
      }
    },
    [
      onError,
      setEditingSourceId,
      setExtractionRuns,
      setLogoSourceUrl,
      setLogoUrl,
      setPage,
      setSelectedCompanyId,
      setSourceUrl,
      setSources,
      setDashboardSources,
    ],
  );

  return { openCompany };
}
