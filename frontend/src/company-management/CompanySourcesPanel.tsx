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
};

export function CompanySourcesPanel({ state, jobs, companies, onboarding }: Props) {
  return (
    <CompanySourcesSection
      sources={state.sources}
      extractionRuns={jobs.extractionRuns}
      decisions={companies.decisions}
      sourceUrl={state.sourceUrl}
      editingSourceId={state.editingSourceId}
      inspection={onboarding.inspection}
      saving={state.saving}
      inspecting={onboarding.inspecting}
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
      }}
    />
  );
}
