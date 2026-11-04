import type { FormEvent } from "react";
import { AppShellHeader } from "./app-shell/AppShellHeader";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { JobsWorkspacePanel } from "./job-management/JobsWorkspacePanel";
import { CompaniesWorkspacePanel } from "./company-management/CompaniesWorkspacePanel";
import { EmployerOnboardingPanel } from "./employer-onboarding/EmployerOnboardingPanel";
import { useScoutApplicationController } from "./useScoutApplicationController";

export default function App() {
  const { state, jobs, companies, onboarding } = useScoutApplicationController();
  const saveBranding = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await companies.saveBranding();
  };

  return (
    <main className="mx-auto flex h-screen max-w-[1600px] flex-col overflow-hidden bg-[#050a14] px-4 pb-3 pt-4 text-white md:px-8">
      <AppShellHeader activePage={state.page} onSelectPage={state.setPage}
        onRefresh={() => void jobs.loadWorkspace()} refreshing={jobs.loading} />
      <OperationalAlerts error={state.error} notice={state.notice} canUndo={jobs.canUndoDecision}
        onUndo={() => void jobs.undoLastDecision()} onDismissError={state.dismissError}
        onDismissNotice={state.dismissNotice} />
      {state.page === "jobs" && <JobsWorkspacePanel
        loading={jobs.loading} extracting={state.extracting} onRefresh={() => void jobs.loadWorkspace()}
        onFetchJobs={() => void jobs.fetchJobs()} vacancies={jobs.vacancies} employers={jobs.employers}
        newVacancies24h={jobs.newVacancies24h} attentionCount={jobs.attentionCount}
        atsPerformance={jobs.atsPerformance} showArchived={state.showArchived}
        onShowArchivedChange={(show) => { state.setShowArchived(show); jobs.clearSelection(); }}
        reviewFilter={state.reviewFilter} onReviewFilterChange={state.setReviewFilter}
        selectedEmployerId={state.selectedEmployerId} onEmployerChange={state.setSelectedEmployerId}
        filteredVacancies={jobs.filteredVacancies} visibleVacancies={jobs.visibleVacancies}
        selectedVacancyId={jobs.selectedVacancyId} openingVacancyId={jobs.openingVacancyId}
        onOpenVacancy={(id, visible) => void jobs.openVacancy(id, visible)}
        selectedVacancy={jobs.selectedVacancy} reviewReason={jobs.reviewReason}
        vacancySaving={jobs.saving} onChangeReviewReason={jobs.setReviewReason}
        onClearSelection={jobs.clearSelection} onDecision={(status) => void jobs.saveDecision(status)}
        onArchive={() => void jobs.archive()} onRestore={() => void jobs.restore()} />}
      {state.page === "companies" && <CompaniesWorkspacePanel
        employers={jobs.employers} dashboardSources={jobs.dashboardSources}
        selectedEmployer={companies.employer} vacancies={jobs.vacancies}
        selectedEmployerId={state.selectedEmployerId} searchQuery={state.companyQuery}
        statusFilter={state.companyStatusFilter} sources={state.sources}
        extractionRuns={jobs.extractionRuns} decisions={companies.decisions}
        logoUrl={state.logoUrl} logoSourceUrl={state.logoSourceUrl} sourceUrl={state.sourceUrl}
        editingSourceId={state.editingSourceId} inspection={onboarding.inspection}
        saving={state.saving} inspecting={onboarding.inspecting}
        onSelectCompany={(employer) => void companies.openCompany(employer)}
        onSearchChange={state.setCompanyQuery} onStatusFilterChange={state.setCompanyStatusFilter}
        onAddCompany={() => { state.setPage("add-company"); state.setError(""); state.setNotice(""); }}
        onUpdateStatus={(status) => void companies.updateStatus(status)}
        onDelete={() => void companies.deleteCompany()} onLogoUrlChange={state.setLogoUrl}
        onLogoSourceUrlChange={state.setLogoSourceUrl} onSaveBranding={saveBranding}
        onEditSource={(source) => { state.setEditingSourceId(source.id); state.setSourceUrl(source.source_url); onboarding.setInspection(null); }}
        onDecisionChange={companies.updateField}
        onSaveDecision={(source) => void companies.saveDecision(source)}
        onChangeSourceUrl={(value) => { state.setSourceUrl(value); onboarding.setInspection(null); }}
        onInspect={() => void onboarding.inspectGreenhouseBoard(state.sourceUrl)}
        onSaveSource={companies.saveSource}
        onCancelEdit={() => { state.setEditingSourceId(null); state.setSourceUrl(""); onboarding.setInspection(null); }} />}
      {state.page === "add-company" && <EmployerOnboardingPanel
        sourceUrl={state.sourceUrl}
        onChangeSourceUrl={(value) => { state.setSourceUrl(value); onboarding.setDiscovery(null); state.setForm((current) => ({ ...current, website_url: value })); }}
        atsKey={onboarding.atsKey}
        onChangeAtsKey={(value) => { onboarding.setAtsKey(value); onboarding.setDiscovery(null); }}
        discovery={onboarding.discovery} onDiscover={onboarding.discover}
        inspecting={onboarding.inspecting} form={state.form}
        onChangeCompanyName={(value) => state.setForm((current) => ({ ...current, name: value }))}
        saving={state.saving} onSubmit={onboarding.submit}
        onCancel={() => { state.setPage("companies"); onboarding.setDiscovery(null); }} />}
      <footer className="mt-5 border-t border-white/15 pt-3 text-[10px] text-white/65">
        Scout is a private operations workspace. Only verified, quality-checked records are eligible
        for publishing to Thungatha.
      </footer>
    </main>
  );
}
