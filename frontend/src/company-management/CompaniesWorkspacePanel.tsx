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

export function CompaniesWorkspacePanel({ state, jobs, companies, onboarding, onSaveBranding }: Props) {
  const selectedEmployer = companies.employer;
  const jobsCount = selectedEmployer
    ? jobs.vacancies.filter((vacancy) => vacancy.employer_id === selectedEmployer.id).length
    : 0;

  return (
    <>
      <p className="mb-3 text-xs text-white/75">
        Manage company identity, verification, branding and registered ATS sources.
      </p>
      <CompanyAttentionActions employers={jobs.employers} sources={jobs.dashboardSources}
        onSelectCompany={(employer) => void companies.openCompany(employer)} />
      <div className="grid min-h-0 gap-3 lg:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.5fr)]">
        <CompanyDirectoryPanel employers={jobs.employers}
          selectedEmployerId={state.selectedEmployerId} searchQuery={state.companyQuery}
          statusFilter={state.companyStatusFilter} onSearchChange={state.setCompanyQuery}
          onStatusFilterChange={state.setCompanyStatusFilter}
          onSelectEmployer={(employer) => void companies.openCompany(employer)}
          onAddCompany={() => {
            state.setPage("add-company");
            state.setError("");
            state.setNotice("");
          }} />
        <CompanyProfilePanel employer={selectedEmployer} jobsCount={jobsCount}
          sources={state.sources} extractionRuns={jobs.extractionRuns} decisions={companies.decisions}
          logoUrl={state.logoUrl} logoSourceUrl={state.logoSourceUrl} sourceUrl={state.sourceUrl}
          editingSourceId={state.editingSourceId} inspection={onboarding.inspection}
          saving={state.saving} inspecting={onboarding.inspecting}
          onUpdateStatus={(status) => void companies.updateStatus(status)}
          onDelete={() => void companies.deleteCompany()}
          onLogoUrlChange={state.setLogoUrl} onLogoSourceUrlChange={state.setLogoSourceUrl}
          onSaveBranding={onSaveBranding}
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
      </div>
    </>
  );
}
