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
  onSaveBranding: (event: FormEvent<HTMLFormElement>) => void;
};

export function CompanyProfilePanel({ state, jobs, companies, onboarding, onSaveBranding }: Props) {
  const employer = companies.employer;
  const [editOpen, setEditOpen] = useState(false);
  if (!employer) return null;
  const runs = state.sources.flatMap((source) => jobs.extractionRuns[source.id] ?? [])
    .filter((run) => run.complete && ["success", "empty"].includes(run.outcome))
    .sort((a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime());
  const jobsCount = jobs.vacancies.filter((item) => item.employer_id === employer.id).length;
  return (
    <section className="flex min-h-0 min-w-0 flex-col overflow-y-auto bg-card p-1">
      <CompanyEditDialog employer={employer} open={editOpen} saving={state.saving}
        onOpenChange={setEditOpen}
        onSave={async (values) => {
          if (await companies.updateDetails(values)) setEditOpen(false);
        }} />
      <CompanyProfileHeader employer={employer} jobsCount={jobsCount}
        sourcesCount={state.sources.length} latestRun={runs[0]} previousRun={runs[1]} />
      <CompanyProfileActions companyName={employer.name} currentStatus={employer.status}
        saving={state.saving} onUpdateStatus={(status) => void companies.updateStatus(status)}
        onDelete={() => void companies.deleteCompany()} onEdit={() => setEditOpen(true)} />
      <CompanyBrandingForm logoUrl={state.logoUrl} logoSourceUrl={state.logoSourceUrl}
        saving={state.saving} onLogoUrlChange={state.setLogoUrl}
        onLogoSourceUrlChange={state.setLogoSourceUrl} onSubmit={onSaveBranding} />
      <CompanySourcesPanel state={state} jobs={jobs} companies={companies} onboarding={onboarding} />
    </section>
  );
}
