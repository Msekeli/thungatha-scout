import type { FormEvent } from "react";
import { scoutApi } from "../api";
import type { Employer } from "../api";
import { useEmployerRegistration } from "./useEmployerRegistration";
import { resolveCareersSource } from "./resolveCareersSource";
import { findEmployerDuplicate } from "./findEmployerDuplicate";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";

type AppState = ReturnType<typeof useScoutAppState>;
type Jobs = ReturnType<typeof useJobsWorkspaceController>;

export function useEmployerOnboardingController(state: AppState, jobs: Jobs) {
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
      jobs.setEmployers((items) =>
        items.some((item) => item.id === employer.id) ? items : [...items, employer],
      );
      jobs.setDashboardSources((items) =>
        items.some((item) => item.id === source.id) ? items : [...items, source],
      );
      state.setSelectedCompanyId(null);
      state.setSources([]);
      state.setPage("companies");
      state.setSourceUrl("");
      state.setForm({ ...state.form, name: "", website_url: "" });
    },
  });

  const duplicate = findEmployerDuplicate(
    state.sourceUrl, state.form.name, jobs.employers, jobs.dashboardSources,
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

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const source = resolveCareersSource(state.sourceUrl, state.form.name);
    if (!source) {
      state.setError("Use a supported Greenhouse, Lever or Teamtailor careers-board URL.");
      return;
    }
    await registration.register(event, source);
  };

  return {
    duplicate,
    openExistingCompany,
    inspection: null,
    setInspection: () => undefined,
    inspecting: false,
    inspectSource: async (url: string) => {
      state.setError("Source inspection is not part of company registration.");
    },
    submit,
  };
}
