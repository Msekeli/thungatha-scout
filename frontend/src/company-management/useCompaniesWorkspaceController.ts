import { useCompanyProfileOperations } from "./useCompanyProfileOperations";
import { useCompanySelection } from "./useCompanySelection";
import { useEmployerSourceReview } from "../employer-sources/useEmployerSourceReview";
import { useEmployerSourceOperations } from "../employer-sources/useEmployerSourceOperations";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";

type AppState = ReturnType<typeof useScoutAppState>;
type Jobs = ReturnType<typeof useJobsWorkspaceController>;

export function useCompaniesWorkspaceController(state: AppState, jobs: Jobs) {
  const employer = jobs.employers.find((item) => item.id === state.selectedEmployerId) ?? null;
  const selection = useCompanySelection({
    setSources: state.setSources,
    setExtractionRuns: jobs.setExtractionRuns,
    setSelectedEmployerId: state.setSelectedEmployerId,
    setLogoUrl: state.setLogoUrl,
    setLogoSourceUrl: state.setLogoSourceUrl,
    setSourceUrl: state.setSourceUrl,
    setEditingSourceId: state.setEditingSourceId,
    setInspection: jobs.setInspection,
    setPage: state.setPage,
    onError: state.setError,
  });
  const profile = useCompanyProfileOperations({
    employer, logoUrl: state.logoUrl, logoSourceUrl: state.logoSourceUrl,
    setEmployers: jobs.setEmployers,
    onDeleted: () => { state.setSelectedEmployerId("all"); state.setSources([]); },
    setSaving: state.setSaving, onNotice: state.setNotice, onError: state.setError,
  });
  const sourceOperations = useEmployerSourceOperations({
    employer, sources: state.sources, setSources: state.setSources,
    sourceUrl: state.sourceUrl, setSourceUrl: state.setSourceUrl,
    editingSourceId: state.editingSourceId, setEditingSourceId: state.setEditingSourceId,
    inspection: jobs.inspection, setInspection: jobs.setInspection,
    setSaving: state.setSaving, onError: state.setError, onNotice: state.setNotice,
  });
  const sourceReview = useEmployerSourceReview({
    employerId: state.selectedEmployerId === "all" ? null : state.selectedEmployerId,
    onSourceUpdated: (updated) => state.setSources((items) =>
      items.map((item) => item.id === updated.id ? updated : item)),
    onDashboardSourceUpdated: (updated) => jobs.setDashboardSources((items) =>
      items.map((item) => item.id === updated.id ? updated : item)),
    setSaving: state.setSaving, onNotice: state.setNotice, onError: state.setError,
  });

  return { employer, ...selection, ...profile, ...sourceOperations, ...sourceReview };
}
