import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";
import type { useCompaniesWorkspaceController } from "./useCompaniesWorkspaceController";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";
import { CompanyDirectoryPanel } from "./CompanyDirectoryPanel";
import { CompanyProfilePanel } from "./CompanyProfilePanel";

type Props = {
  state: ReturnType<typeof useScoutAppState>;
  jobs: ReturnType<typeof useJobsWorkspaceController>;
  companies: ReturnType<typeof useCompaniesWorkspaceController>;
  onboarding: ReturnType<typeof useEmployerOnboardingController>;
  currentJobsByEmployer: Record<string, number>;
  jobChangesByEmployer: Record<string, number>;
};

export function CompaniesWorkspacePanel({
  state, jobs, companies, onboarding, currentJobsByEmployer, jobChangesByEmployer,
}: Props) {
  const selectCompany = (employer: Parameters<typeof companies.openCompany>[0]) => {
    void companies.openCompany(employer);
  };
  const hasSelection = Boolean(companies.employer);
  return (
    <section className={
      "grid min-h-0 flex-1 gap-4 overflow-hidden pt-4 " +
      (hasSelection ? "lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.85fr)]" : "grid-cols-1")
    }>
      <CompanyDirectoryPanel
        employers={jobs.employers}
        sources={jobs.dashboardSources}
        selectedEmployerId={state.selectedCompanyId ?? ""}
        searchQuery={state.companyQuery}
        sourceFilter={state.companySourceFilter}
        currentJobsByEmployer={currentJobsByEmployer}
        jobChangesByEmployer={jobChangesByEmployer}
        onSearchChange={state.setCompanyQuery}
        onSourceFilterChange={state.setCompanySourceFilter}
        onSelectEmployer={selectCompany}
        onAddCompany={() => {
          state.setError("");
          state.setNotice("");
          state.setPage("add-company");
        }}
      />
      {hasSelection && (
        <aside className="min-h-0 overflow-y-auto rounded-xl border p-4 scout-company-dialog">
          <CompanyProfilePanel
            state={state}
            jobs={jobs}
            companies={companies}
            onboarding={onboarding}
          />
        </aside>
      )}
    </section>
  );
}
