import type { FormEvent } from "react";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";
import type { useCompaniesWorkspaceController } from "./useCompaniesWorkspaceController";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";
import { CompanyAttentionActions } from "./CompanyAttentionActions";
import { CompanyDirectoryPanel } from "./CompanyDirectoryPanel";
import { CompanyProfilePanel } from "./CompanyProfilePanel";

type Props = {
  state: ReturnType<typeof useScoutAppState>;
  jobs: ReturnType<typeof useJobsWorkspaceController>;
  companies: ReturnType<typeof useCompaniesWorkspaceController>;
  onboarding: ReturnType<typeof useEmployerOnboardingController>;
  onSaveBranding: (event: FormEvent<HTMLFormElement>) => void;
};

export function CompaniesWorkspacePanel({
  state,
  jobs,
  companies,
  onboarding,
  onSaveBranding,
}: Props) {
  const selectedEmployer = companies.employer;
  const jobsCount = selectedEmployer
    ? jobs.vacancies.filter((vacancy) => vacancy.employer_id === selectedEmployer.id).length
    : 0;
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden pt-4">
      <CompanyAttentionActions
        employers={jobs.employers}
        sources={jobs.dashboardSources}
        onSelectCompany={(employer) => void companies.openCompany(employer)}
      />
      <div className="grid min-h-0 flex-1 gap-4 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.85fr)]">
        <CompanyDirectoryPanel
          employers={jobs.employers}
          sources={jobs.dashboardSources}
          selectedEmployerId={state.selectedEmployerId}
          searchQuery={state.companyQuery}
          statusFilter={state.companyStatusFilter}
          onSearchChange={state.setCompanyQuery}
          onStatusFilterChange={state.setCompanyStatusFilter}
          onSelectEmployer={(employer) => void companies.openCompany(employer)}
          onAddCompany={() => {
            state.setError("");
            state.setNotice("");
            state.setPage("add-company");
          }}
        />
        <CompanyProfilePanel
          state={state}
          jobs={jobs}
          companies={companies}
          onboarding={onboarding}
          jobsCount={jobsCount}
          onSaveBranding={onSaveBranding}
        />
      </div>
    </section>
  );
}
