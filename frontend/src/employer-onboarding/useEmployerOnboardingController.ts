import type { FormEvent } from "react";
import { useCareersDiscovery } from "./useCareersDiscovery";
import { useEmployerRegistration } from "./useEmployerRegistration";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";

type AppState = ReturnType<typeof useScoutAppState>;
type Jobs = ReturnType<typeof useJobsWorkspaceController>;

export function useEmployerOnboardingController(state: AppState, jobs: Jobs) {
  const discovery = useCareersDiscovery({ onError: state.setError });
  const registration = useEmployerRegistration({
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
      state.setForm({ ...state.form, name: "", website_url: "" });
    },
  });

  const fillDetectedCompany = (name: string) =>
    state.setForm((current) => ({ ...current, name: current.name || name }));

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const result = await discovery.discover(
      state.sourceUrl,
      state.form.name,
      fillDetectedCompany,
    );
    if (result) await registration.register(event, result);
  };

  return { inspecting: discovery.inspecting, submit };
}
