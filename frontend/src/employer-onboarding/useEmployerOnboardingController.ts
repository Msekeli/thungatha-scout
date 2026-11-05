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
    onRegistered: ({ employer, source }) => {
      state.setSelectedEmployerId(employer.id);
      state.setSources([source]);
      state.setPage("companies");
      state.setSourceUrl("");
      discovery.setDiscovery(null);
      state.setForm({ ...state.form, name: "", website_url: "" });
    },
  });

  const setCompanyName = (name: string) =>
    state.setForm((current) => ({ ...current, name }));
  const fillDetectedCompany = (name: string) =>
    state.setForm((current) => ({
      ...current,
      name: current.name || name,
    }));
  const discover = () =>
    void discovery.discover(state.sourceUrl, state.form.name, fillDetectedCompany);
  const submit = (event: FormEvent<HTMLFormElement>) => {
    if (discovery.discovery) {
      void registration.register(event);
      return;
    }
    event.preventDefault();
    discover();
  };

  return {
    ...discovery,
    register: registration.register,
    discover,
    submit,
    updateDetectedCompany: setCompanyName,
  };
}
