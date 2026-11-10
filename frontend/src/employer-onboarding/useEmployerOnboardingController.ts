import type { FormEvent } from "react";
import { scoutApi } from "../api";
import type { Employer } from "../api";
import { useCareersDiscovery } from "./useCareersDiscovery";
import { useEmployerRegistration } from "./useEmployerRegistration";
import { findEmployerDuplicate } from "./findEmployerDuplicate";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";

type AppState = ReturnType<typeof useScoutAppState>;
type Jobs = ReturnType<typeof useJobsWorkspaceController>;

export function useEmployerOnboardingController(state: AppState, jobs: Jobs) {
  const discovery = useCareersDiscovery({ onError: state.setError });
  const registration = useEmployerRegistration({
    form: state.form,
    sourceUrl: state.sourceUrl,
    employers: jobs.employers,
    sources: jobs.dashboardSources,
    loadWorkspace: jobs.loadWorkspace,
    setSaving: state.setSaving,
    onError: state.setError,
    onNotice: state.setNotice,
    onRegistered: ({ employer, source }) => {
      state.setSelectedCompanyId(employer.id);
      state.setSources([source]);
      state.setPage("companies");
      state.setSourceUrl("");
      state.setForm({ ...state.form, name: "", website_url: "" });
    },
  });

  const duplicate = findEmployerDuplicate(
    state.sourceUrl,
    state.form.name,
    jobs.employers,
    jobs.dashboardSources,
  );

  const openExistingCompany = async (employerId: string) => {
    const employer = jobs.employers.find((item) => item.id === employerId);
    if (!employer) return;
    state.setSelectedCompanyId(employerId);
    state.setPage("companies");
    try {
      state.setSources(await scoutApi.listSources(employerId));
    } catch (reason) {
      state.setError(reason instanceof Error ? reason.message : "Could not load company sources.");
    }
  };

  const fillDetectedCompany = (name: string) =>
    state.setForm((current) => ({ ...current, name: current.name || name }));

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const result = await discovery.discover(state.sourceUrl, state.form.name, fillDetectedCompany);
    if (result) await registration.register(event, result);
  };

  return {
    duplicate,
    openExistingCompany,
    inspection: discovery.inspection,
    setInspection: discovery.setInspection,
    inspecting: discovery.inspecting,
    inspectSource: discovery.inspectSource,
    submit,
  };
}
