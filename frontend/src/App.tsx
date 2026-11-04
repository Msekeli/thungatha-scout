import type { FormEvent } from "react";
import { AppShellHeader } from "./app-shell/AppShellHeader";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { useCompanyProfileOperations } from "./company-management/useCompanyProfileOperations";
import { CompaniesWorkspacePanel } from "./company-management/CompaniesWorkspacePanel";
import { useCompanySelection } from "./company-management/useCompanySelection";
import { useEmployerSourceReview } from "./employer-sources/useEmployerSourceReview";
import { useEmployerSourceOperations } from "./employer-sources/useEmployerSourceOperations";
import { useVacancyReview } from "./job-management/useVacancyReview";
import { JobsWorkspacePanel } from "./job-management/JobsWorkspacePanel";
import { EmployerOnboardingPanel } from "./employer-onboarding/EmployerOnboardingPanel";
import { useScoutWorkspace } from "./useScoutWorkspace";
import { useScoutDashboardMetrics } from "./useScoutDashboardMetrics";
import { useVacancyFetching } from "./useVacancyFetching";
import { useCareersDiscovery } from "./employer-onboarding/useCareersDiscovery";
import { emptyEmployer, useScoutAppState } from "./app-shell/useScoutAppState";
import { useEmployerRegistration } from "./employer-onboarding/useEmployerRegistration";

export default function App() {
  const {
    page, setPage, showArchived, setShowArchived, reviewFilter, setReviewFilter,
    logoUrl, setLogoUrl, logoSourceUrl, setLogoSourceUrl, companyQuery, setCompanyQuery,
    companyStatusFilter, setCompanyStatusFilter, selectedEmployerId, setSelectedEmployerId,
    sources, setSources, form, setForm, sourceUrl, setSourceUrl, editingSourceId,
    setEditingSourceId, extracting, setExtracting, saving, setSaving, error, setError,
    notice, setNotice, dismissError, dismissNotice,
  } = useScoutAppState();

  const {
    discovery,
    setDiscovery,
    inspection,
    setInspection,
    atsKey,
    setAtsKey,
    inspecting,
    discover,
    inspectGreenhouseBoard,
  } = useCareersDiscovery({ onError: setError, onNotice: setNotice });

  const {
    employers,
    setEmployers,
    vacancies,
    setVacancies,
    archivedVacancies,
    dashboardSources,
    setDashboardSources,
    extractionRuns,
    setExtractionRuns,
    loading,
    loadWorkspace,
  } = useScoutWorkspace(setError);

  const {
    selectedVacancy,
    selectedVacancyId,
    openingVacancyId,
    reviewReason,
    setReviewReason,
    saving: vacancySaving,
    openVacancy,
    saveDecision: setVacancyDecision,
    undoLastDecision,
    canUndoDecision,
    archive: archiveSelectedVacancy,
    restore: restoreSelectedVacancy,
    clearSelection,
  } = useVacancyReview({
    onVacancyUpdated: (updated) =>
      setVacancies((current) => current.map((item) => (item.id === updated.id ? updated : item))),
    onRefresh: loadWorkspace,
    onNotice: setNotice,
    onError: setError,
  });

  const selectedEmployer = employers.find((item) => item.id === selectedEmployerId) ?? null;
  const { register: registerDiscoveredEmployer } = useEmployerRegistration({
    discovery,
    form,
    sourceUrl,
    loadWorkspace,
    setSaving,
    onError: setError,
    onNotice: setNotice,
    onRegistered: ({ employer, source, run }) => {
      setSelectedEmployerId(employer.id);
      setSources([source]);
      setExtractionRuns((current) => ({ ...current, [source.id]: [run] }));
      setPage("companies");
      setSourceUrl("");
      setDiscovery(null);
      setForm(emptyEmployer);
    },
  });
  const { saveSource } = useEmployerSourceOperations({
    employer: selectedEmployer,
    sources,
    setSources,
    sourceUrl,
    setSourceUrl,
    editingSourceId,
    setEditingSourceId,
    inspection,
    setInspection,
    setSaving,
    onError: setError,
    onNotice: setNotice,
  });
  const {
    updateStatus: updateCompanyStatus,
    deleteCompany,
    saveBranding,
  } = useCompanyProfileOperations({
    employer: selectedEmployer,
    logoUrl,
    logoSourceUrl,
    setEmployers,
    onDeleted: () => {
      setSelectedEmployerId("all");
      setSources([]);
    },
    setSaving,
    onNotice: setNotice,
    onError: setError,
  });
  const {
    decisions: sourceDecision,
    updateField: updateSourceDecisionField,
    saveDecision: saveSourceDecision,
  } = useEmployerSourceReview({
    employerId: selectedEmployerId === "all" ? null : selectedEmployerId,
    onSourceUpdated: (updated) =>
      setSources((current) => current.map((item) => (item.id === updated.id ? updated : item))),
    onDashboardSourceUpdated: (updated) =>
      setDashboardSources((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      ),
    setSaving,
    onNotice: setNotice,
    onError: setError,
  });
  const { fetchJobs } = useVacancyFetching({
    dashboardSources,
    setExtracting,
    loadWorkspace,
    onError: setError,
    onNotice: setNotice,
  });

  const { openCompany } = useCompanySelection({
    setSources,
    setExtractionRuns,
    setSelectedEmployerId,
    setLogoUrl,
    setLogoSourceUrl,
    setSourceUrl,
    setEditingSourceId,
    setInspection,
    setPage,
    onError: setError,
  });

  const { newVacancies24h, attentionCount, atsPerformance, visibleVacancies, filteredVacancies } =
    useScoutDashboardMetrics({
      employers,
      vacancies,
      archivedVacancies,
      dashboardSources,
      extractionRuns,
      showArchived,
      selectedEmployerId,
      reviewFilter,
    });

  async function saveEmployerBranding(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await saveBranding();
  }

  function handleEmployerOnboardingSubmit(event: FormEvent<HTMLFormElement>) {
    if (discovery) {
      void registerDiscoveredEmployer(event);
      return;
    }

    event.preventDefault();
    void discover(sourceUrl, (detectedName) =>
      setForm((current) => ({
        ...current,
        name: current.name || detectedName,
        website_url: sourceUrl,
      })),
    );
  }

  function handleEmployerDiscovery() {
    void discover(sourceUrl, (detectedName) =>
      setForm((current) => ({
        ...current,
        name: current.name || detectedName,
        website_url: sourceUrl,
      })),
    );
  }

  return (
    <main className="mx-auto flex h-screen max-w-[1600px] flex-col overflow-hidden bg-[#050a14] px-4 pb-3 pt-4 text-white md:px-8">
      <AppShellHeader
        activePage={page}
        onSelectPage={setPage}
        onRefresh={() => void loadWorkspace()}
        refreshing={loading}
      />

      <OperationalAlerts
        error={error}
        notice={notice}
        canUndo={canUndoDecision}
        onUndo={() => void undoLastDecision()}
        onDismissError={dismissError}
        onDismissNotice={dismissNotice}
      />

      {page === "jobs" && (
        <JobsWorkspacePanel
          loading={loading}
          extracting={extracting}
          onRefresh={() => void loadWorkspace()}
          onFetchJobs={() => void fetchJobs()}
          vacancies={vacancies}
          employers={employers}
          newVacancies24h={newVacancies24h}
          attentionCount={attentionCount}
          atsPerformance={atsPerformance}
          showArchived={showArchived}
          onShowArchivedChange={(show) => {
            setShowArchived(show);
            clearSelection();
          }}
          reviewFilter={reviewFilter}
          onReviewFilterChange={setReviewFilter}
          selectedEmployerId={selectedEmployerId}
          onEmployerChange={setSelectedEmployerId}
          filteredVacancies={filteredVacancies}
          visibleVacancies={visibleVacancies}
          selectedVacancyId={selectedVacancyId}
          openingVacancyId={openingVacancyId}
          onOpenVacancy={(vacancyId, visible) => void openVacancy(vacancyId, visible)}
          selectedVacancy={selectedVacancy}
          reviewReason={reviewReason}
          vacancySaving={vacancySaving}
          onChangeReviewReason={setReviewReason}
          onClearSelection={clearSelection}
          onDecision={(status) => void setVacancyDecision(status)}
          onArchive={() => void archiveSelectedVacancy()}
          onRestore={() => void restoreSelectedVacancy()}
        />
      )}

      {page === "companies" && (
        <CompaniesWorkspacePanel
          employers={employers}
          dashboardSources={dashboardSources}
          selectedEmployer={selectedEmployer}
          vacancies={vacancies}
          selectedEmployerId={selectedEmployerId}
          searchQuery={companyQuery}
          statusFilter={companyStatusFilter}
          sources={sources}
          extractionRuns={extractionRuns}
          decisions={sourceDecision}
          logoUrl={logoUrl}
          logoSourceUrl={logoSourceUrl}
          sourceUrl={sourceUrl}
          editingSourceId={editingSourceId}
          inspection={inspection}
          saving={saving}
          inspecting={inspecting}
          onSelectCompany={(employer) => void openCompany(employer)}
          onSearchChange={setCompanyQuery}
          onStatusFilterChange={setCompanyStatusFilter}
          onAddCompany={() => {
            setPage("add-company");
            setError("");
            setNotice("");
          }}
          onUpdateStatus={(status) => void updateCompanyStatus(status)}
          onDelete={() => void deleteCompany()}
          onLogoUrlChange={setLogoUrl}
          onLogoSourceUrlChange={setLogoSourceUrl}
          onSaveBranding={saveEmployerBranding}
          onEditSource={(source) => {
            setEditingSourceId(source.id);
            setSourceUrl(source.source_url);
            setInspection(null);
          }}
          onDecisionChange={updateSourceDecisionField}
          onSaveDecision={(source) => void saveSourceDecision(source)}
          onChangeSourceUrl={(value) => {
            setSourceUrl(value);
            setInspection(null);
          }}
          onInspect={() => void inspectGreenhouseBoard(sourceUrl)}
          onSaveSource={saveSource}
          onCancelEdit={() => {
            setEditingSourceId(null);
            setSourceUrl("");
            setInspection(null);
          }}
        />
      )}

      {page === "add-company" && (
        <EmployerOnboardingPanel
          sourceUrl={sourceUrl}
          onChangeSourceUrl={(value) => {
            setSourceUrl(value);
            setDiscovery(null);
            setForm((current) => ({ ...current, website_url: value }));
          }}
          atsKey={atsKey}
          onChangeAtsKey={(value) => {
            setAtsKey(value);
            setDiscovery(null);
          }}
          discovery={discovery}
          onDiscover={handleEmployerDiscovery}
          inspecting={inspecting}
          form={form}
          onChangeCompanyName={(value) => setForm((current) => ({ ...current, name: value }))}
          saving={saving}
          onSubmit={handleEmployerOnboardingSubmit}
          onCancel={() => {
            setPage("companies");
            setDiscovery(null);
          }}
        />
      )}

      <footer className="mt-5 border-t border-white/15 pt-3 text-[10px] text-white/65">
        Scout is a private operations workspace. Only verified, quality-checked records are eligible
        for publishing to Thungatha.
      </footer>
    </main>
  );
}
