import { useScoutAppState } from "./app-state/useScoutAppState";
import { useJobsWorkspaceController } from "./job-management/useJobsWorkspaceController";
import { useCompaniesWorkspaceController } from "./company-management/useCompaniesWorkspaceController";
import { useEmployerOnboardingController } from "./employer-onboarding/useEmployerOnboardingController";

export function useScoutApplicationController() {
  const state = useScoutAppState();
  const jobs = useJobsWorkspaceController(state);
  const companies = useCompaniesWorkspaceController(state, jobs);
  const onboarding = useEmployerOnboardingController(state, jobs);
  return { state, jobs, companies, onboarding };
}
