import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
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
  state,
  jobs,
  companies,
  onboarding,
  currentJobsByEmployer,
  jobChangesByEmployer,
}: Props) {
  const selectCompany = (employer: Parameters<typeof companies.openCompany>[0]) => {
    void companies.openCompany(employer);
  };

  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden pt-4">
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
      <Dialog
        open={!!companies.employer}
        onOpenChange={(open) => {
          if (!open) {
            state.setSelectedCompanyId(null);
            state.setSources([]);
          }
        }}
      >
        <DialogContent
          className="scout-company-dialog !max-h-[86vh] !w-[min(95vw,58rem)] !max-w-none !overflow-hidden !p-0"
          overlayClassName="!bg-transparent !backdrop-blur-0"
        >
          <DialogHeader className="scout-company-dialog-header">
            <DialogTitle className="scout-company-heading">Company details</DialogTitle>
          </DialogHeader>
          <CompanyProfilePanel
            state={state}
            jobs={jobs}
            companies={companies}
            onboarding={onboarding}
          />
        </DialogContent>
      </Dialog>
    </section>
  );
}
