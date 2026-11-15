import { useEffect } from "react";
import { useCompanyProfileOperations } from "./useCompanyProfileOperations";
import { useCompanyDetailsUpdate } from "./useCompanyDetailsUpdate";
import { useCompanySelection } from "./useCompanySelection";
import { useEmployerSourceOperations } from "../employer-sources/useEmployerSourceOperations";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";

type AppState = ReturnType<typeof useScoutAppState>;
type Jobs = ReturnType<typeof useJobsWorkspaceController>;
type Onboarding = ReturnType<typeof useEmployerOnboardingController>;

export function useCompaniesWorkspaceController(
  state: AppState,
  jobs: Jobs,
  onboarding: Onboarding,
) {
  const employer = jobs.employers.find((item) => item.id === state.selectedCompanyId) ?? null;
  const selection = useCompanySelection({
    setSources: state.setSources,
    dashboardSources: jobs.dashboardSources,
    setSelectedCompanyId: state.setSelectedCompanyId,
    setLogoUrl: state.setLogoUrl,
    setLogoSourceUrl: state.setLogoSourceUrl,
    setSourceUrl: state.setSourceUrl,
    setEditingSourceId: state.setEditingSourceId,
    setPage: state.setPage,
    onError: state.setError,
  });
  useEffect(() => {
    if (!state.selectedCompanyId) return;
    state.setSources(
      jobs.dashboardSources.filter((source) => source.employer_id === state.selectedCompanyId),
    );
  }, [jobs.dashboardSources, state.selectedCompanyId, state.setSources]);

  const profile = useCompanyProfileOperations({
    employer,
    logoUrl: state.logoUrl,
    logoSourceUrl: state.logoSourceUrl,
    setEmployers: jobs.setEmployers,
    onDeleted: () => {
      state.setSelectedCompanyId(null);
      state.setSources([]);
      jobs.setDashboardSources((items) =>
        items.filter((item) => item.employer_id !== employer?.id),
      );
      jobs.setVacancies((items) => items.filter((item) => item.employer_id !== employer?.id));
      jobs.setArchivedVacancies((items) =>
        items.filter((item) => item.employer_id !== employer?.id),
      );
    },
    setSaving: state.setSaving,
    onNotice: state.setNotice,
    onError: state.setError,
  });
  const updateDetails = useCompanyDetailsUpdate({
    employer,
    setEmployers: jobs.setEmployers,
    setSaving: state.setSaving,
    onNotice: state.setNotice,
    onError: state.setError,
  });
  const sourceOperations = useEmployerSourceOperations({
    employer,
    setSources: state.setSources,
    sourceUrl: state.sourceUrl,
    setSourceUrl: state.setSourceUrl,
    editingSourceId: state.editingSourceId,
    setEditingSourceId: state.setEditingSourceId,
    inspection: onboarding.inspection,
    setInspection: onboarding.setInspection,
    setSaving: state.setSaving,
    onError: state.setError,
    onNotice: state.setNotice,
  });
  return { employer, ...selection, ...profile, updateDetails, ...sourceOperations };
}
