import { useState } from "react";
import type { FormEvent } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
  onSaveBranding: (event: FormEvent<HTMLFormElement>) => void;
};

export function CompaniesWorkspacePanel({
  state,
  jobs,
  companies,
  onboarding,
  onSaveBranding,
}: Props) {
  const [profileOpen, setProfileOpen] = useState(false);
  const selectCompany = (employer: Parameters<typeof companies.openCompany>[0]) => {
    void companies.openCompany(employer);
    setProfileOpen(true);
  };
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden pt-4">
      <CompanyDirectoryPanel
        employers={jobs.employers}
        sources={jobs.dashboardSources}
        selectedEmployerId={state.selectedEmployerId}
        searchQuery={state.companyQuery}
        sourceFilter={state.companySourceFilter}
        extractionRuns={jobs.extractionRuns}
        onSearchChange={state.setCompanyQuery}
        onSourceFilterChange={state.setCompanySourceFilter}
        onSelectEmployer={selectCompany}
        onAddCompany={() => {
          state.setError("");
          state.setNotice("");
          state.setPage("add-company");
        }}
      />
      <Dialog open={profileOpen && !!companies.employer} onOpenChange={setProfileOpen}>
        <DialogContent className="scout-company-dialog">
          <DialogHeader>
            <DialogTitle className="scout-company-heading">Company details</DialogTitle>
            <DialogDescription className="scout-company-muted">
              Review company information, job production, sources and extraction history.
            </DialogDescription>
          </DialogHeader>
          <CompanyProfilePanel
            state={state}
            jobs={jobs}
            companies={companies}
            onboarding={onboarding}
            onSaveBranding={onSaveBranding}
          />
        </DialogContent>
      </Dialog>
    </section>
  );
}
