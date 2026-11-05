import type { FormEvent } from "react";
import { useCareersDiscovery } from "./useCareersDiscovery";
import { useEmployerRegistration } from "./useEmployerRegistration";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";

type AppState = ReturnType<typeof useScoutAppState>;
type Jobs = ReturnType<typeof useJobsWorkspaceController>;

export function useEmployerOnboardingController(state: AppState, jobs: Jobs) {
  const discovery = useCareersDiscovery({ onError: state.setError, onNotice: state.setNotice });
  const registration = useEmployerRegistration({
    discovery: discovery.discovery,
    form: state.form,
    sourceUrl: state.sourceUrl,
    loadWorkspace: jobs.loadWorkspace,
    setSaving: state.setSaving,
    onError: state.setError,
    onNotice: state.setNotice,
    onRegistered: ({ employer, source, run }) => {
      state.setSelectedEmployerId(employer.id);
      state.setSources([source]);
      jobs.setExtractionRuns((items) => ({ ...items, [source.id]: [run] }));
      state.setPage("companies");
      state.setSourceUrl("");
      discovery.setDiscovery(null);
      state.setForm({ ...state.form, name: "", website_url: "" });
    },
  });

  const updateDetectedCompany = (name: string) =>
    state.setForm((current) => ({
      ...current,
      name: current.name || name,
    }));
  const discover = () => void discovery.discover(state.sourceUrl, updateDetectedCompany);
  const submit = (event: FormEvent<HTMLFormElement>) => {
    if (discovery.discovery) {
      void registration.register(event);
      return;
    }
    event.preventDefault();
    void discovery.discover(state.sourceUrl, updateDetectedCompany);
  };

  return { ...discovery, register: registration.register, discover, submit, updateDetectedCompany };
}
