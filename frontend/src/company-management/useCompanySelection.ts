import { useCallback } from "react";
import type { Dispatch, SetStateAction } from "react";
import type { Employer, EmployerSource } from "../api";

type UseCompanySelectionOptions = {
  dashboardSources: EmployerSource[];
  setSources: Dispatch<SetStateAction<EmployerSource[]>>;
  setSelectedCompanyId: (id: string | null) => void;
  setLogoUrl: (url: string) => void;
  setLogoSourceUrl: (url: string) => void;
  setSourceUrl: (url: string) => void;
  setEditingSourceId: (id: string | null) => void;
  setPage: (page: "companies") => void;
  onError: (message: string) => void;
};

export function useCompanySelection({
  dashboardSources,
  setSources,
  setSelectedCompanyId,
  setLogoUrl,
  setLogoSourceUrl,
  setSourceUrl,
  setEditingSourceId,
  setPage,
  onError,
}: UseCompanySelectionOptions) {
  const openCompany = useCallback(
    (employer: Employer) => {
      setEditingSourceId(null);
      setSourceUrl("");
      setSources(dashboardSources.filter((source) => source.employer_id === employer.id));
      setSelectedCompanyId(employer.id);
      setLogoUrl(employer.logo_url ?? "");
      setLogoSourceUrl(employer.logo_source_url ?? "");
      setPage("companies");
      onError("");
    },
    [
      dashboardSources,
      onError,
      setEditingSourceId,
      setLogoSourceUrl,
      setLogoUrl,
      setPage,
      setSelectedCompanyId,
      setSourceUrl,
      setSources,
    ],
  );

  return { openCompany };
}
