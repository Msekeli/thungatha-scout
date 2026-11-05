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
  const sourceRuns = state.sources.map((source) =>
    (jobs.extractionRuns[source.id] ?? [])
      .filter((run) => run.complete && ["success", "empty"].includes(run.outcome))
      .sort(
        (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
      ),
  );
  const latestRuns = sourceRuns.flatMap((runs) => runs.slice(0, 1));
  const canCompare = sourceRuns.length > 0 && sourceRuns.every((runs) => runs.length > 1);
  const latestJobs = latestRuns.length
    ? latestRuns.reduce((total, run) => total + run.jobs_received, 0)
    : null;
  const previousJobs = canCompare
    ? sourceRuns.reduce((total, runs) => total + runs[1].jobs_received, 0)
    : null;
  const lastRunAt =
    latestRuns
      .map((run) => run.finished_at ?? run.started_at ?? "")
      .filter(Boolean)
      .sort()
      .at(-1) ?? null;
  const jobsCount = jobs.vacancies.filter((item) => item.employer_id === employer.id).length;
  return (
    <section className="flex min-h-0 min-w-0 flex-col overflow-y-auto bg-transparent p-1 scout-company-heading">
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
        careersUrl={
          state.sources.find((source) => source.employer_careers_url)?.employer_careers_url ??
          employer.website_url ??
          null
        }
        jobsCount={jobsCount}
        sourcesCount={state.sources.length}
        latestJobs={latestJobs}
        previousJobs={previousJobs}
        lastRunAt={lastRunAt}
      />
      <CompanyProfileActions
        companyName={employer.name}
        saving={state.saving}
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
    </section>
  );
}
