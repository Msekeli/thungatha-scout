import type { FormEvent } from "react";
import { CompanyProfileActions } from "./CompanyProfileActions";
import { CompanyProfileHeader } from "./CompanyProfileHeader";
import { CompanyBrandingForm } from "./CompanyBrandingForm";
import { CompanySourcesSection } from "../employer-sources/CompanySourcesSection";
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

export function CompanyProfilePanel({ state, jobs, companies, onboarding, jobsCount, onSaveBranding }: Props) {
  const employer = companies.employer;
  return (
    <section className="min-w-0 rounded-xl border border-border bg-card p-4 shadow-sm">
      {employer ? (
        <>
          <CompanyProfileHeader employer={employer} jobsCount={jobsCount}
            sourcesCount={state.sources.length} />
          <CompanyProfileActions currentStatus={employer.status} saving={state.saving}
            onUpdateStatus={(status) => void companies.updateStatus(status)}
            onDelete={() => void companies.deleteCompany()} />
          <CompanyBrandingForm logoUrl={state.logoUrl} logoSourceUrl={state.logoSourceUrl}
            saving={state.saving} onLogoUrlChange={state.setLogoUrl}
            onLogoSourceUrlChange={state.setLogoSourceUrl} onSubmit={onSaveBranding} />
          <CompanySourcesSection sources={state.sources} extractionRuns={jobs.extractionRuns}
            decisions={companies.decisions} sourceUrl={state.sourceUrl}
            editingSourceId={state.editingSourceId} inspection={onboarding.inspection}
            saving={state.saving} inspecting={onboarding.inspecting}
            onEditSource={(source) => {
              state.setEditingSourceId(source.id);
              state.setSourceUrl(source.source_url);
              onboarding.setInspection(null);
            }}
            onDecisionChange={companies.updateField}
            onSaveDecision={(source) => void companies.saveDecision(source)}
            onChangeSourceUrl={(value) => {
              state.setSourceUrl(value);
              onboarding.setInspection(null);
            }}
            onInspect={() => void onboarding.inspectGreenhouseBoard(state.sourceUrl)}
            onSaveSource={companies.saveSource}
            onCancelEdit={() => {
              state.setEditingSourceId(null);
              state.setSourceUrl("");
              onboarding.setInspection(null);
            }} />
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
