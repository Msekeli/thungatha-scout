import { useState } from "react";
import type { FormEvent } from "react";
import { CompanyProfileActions } from "./CompanyProfileActions";
import { CompanyEditDialog } from "./CompanyEditDialog";
import { CompanyProfileHeader } from "./CompanyProfileHeader";
import { CompanyBrandingForm } from "./CompanyBrandingForm";
import { CompanySourcesPanel } from "./CompanySourcesPanel";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";
import type { useCompaniesWorkspaceController } from "./useCompaniesWorkspaceController";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";

type Props = {
  state: ReturnType<typeof useScoutAppState>;
  jobs: ReturnType<typeof useJobsWorkspaceController>;
  companies: ReturnType<typeof useCompaniesWorkspaceController>;
  onboarding: ReturnType<typeof useEmployerOnboardingController>;
  jobsCount: number;
  onSaveBranding: (event: FormEvent<HTMLFormElement>) => void;
};

export function CompanyProfilePanel({
  state,
  jobs,
  companies,
  onboarding,
  jobsCount,
  onSaveBranding,
}: Props) {
  const employer = companies.employer;
  const [editOpen, setEditOpen] = useState(false);
  return (
    <section className="flex min-h-0 min-w-0 flex-col overflow-y-auto rounded-xl border border-border bg-card p-4 shadow-sm">
      {employer ? (
        <>
          <CompanyEditDialog
            employer={employer}
            open={editOpen}
            saving={state.saving}
            onOpenChange={setEditOpen}
            onSave={async (values) => {
              if (await companies.updateDetails(values)) setEditOpen(false);
            }}
          />
          <CompanyProfileHeader
            employer={employer}
            jobsCount={jobsCount}
            sourcesCount={state.sources.length}
          />
          <CompanyProfileActions
            currentStatus={employer.status}
            saving={state.saving}
            onUpdateStatus={(status) => void companies.updateStatus(status)}
            onDelete={() => void companies.deleteCompany()}
            onEdit={() => setEditOpen(true)}
          />
          <CompanyBrandingForm
            logoUrl={state.logoUrl}
            logoSourceUrl={state.logoSourceUrl}
            saving={state.saving}
            onLogoUrlChange={state.setLogoUrl}
            onLogoSourceUrlChange={state.setLogoSourceUrl}
            onSubmit={onSaveBranding}
          />
          <CompanySourcesPanel
            state={state}
            jobs={jobs}
            companies={companies}
            onboarding={onboarding}
          />
        </>
      ) : (
        <div className="grid min-h-[260px] content-center gap-2 px-6 text-center text-sm text-muted-foreground">
          <strong>Select a company</strong>
          <span>Choose a company to view its profile and registered job sources.</span>
        </div>
      )}
    </section>
  );
}
