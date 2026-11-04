import { useState } from "react";
import { BriefcaseBusiness, RefreshCw } from "lucide-react";
import type { FormEvent } from "react";
import type { EmployerSource } from "./api";
import { Badge } from "@/components/ui/badge";
import { AppShellHeader } from "./app-shell/AppShellHeader";
import { CompanyAttentionActions } from "./company-management/CompanyAttentionActions";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CompanyProfileActions } from "./company-management/CompanyProfileActions";
import { CompanyDirectoryList } from "./company-management/CompanyDirectoryList";
import { CompanySearchFilters } from "./company-management/CompanySearchFilters";
import { CompanyProfileHeader } from "./company-management/CompanyProfileHeader";
import { CompanyBrandingForm } from "./company-management/CompanyBrandingForm";
import { useCompanyProfileOperations } from "./company-management/useCompanyProfileOperations";
import { useCompanySelection } from "./company-management/useCompanySelection";
import { CompanySourcesSection } from "./employer-sources/CompanySourcesSection";
import { useEmployerSourceReview } from "./employer-sources/useEmployerSourceReview";
import { useEmployerSourceOperations } from "./employer-sources/useEmployerSourceOperations";
import { VacancyDetailsPanel } from "./job-management/VacancyDetailsPanel";
import { VacancyRecordList } from "./job-management/VacancyRecordList";
import { VacancyRecordsToolbar } from "./job-management/VacancyRecordsToolbar";
import { useVacancyReview } from "./job-management/useVacancyReview";
import { OnboardingUrlForm } from "./employer-onboarding/OnboardingUrlForm";
import { OnboardingPreviewCard } from "./employer-onboarding/OnboardingPreviewCard";
import { useScoutWorkspace } from "./useScoutWorkspace";
import { useScoutDashboardMetrics } from "./useScoutDashboardMetrics";
import { DashboardOverview } from "./app-shell/DashboardOverview";
import { useVacancyFetching } from "./useVacancyFetching";
import { useCareersDiscovery } from "./employer-onboarding/useCareersDiscovery";
import { useEmployerRegistration } from "./employer-onboarding/useEmployerRegistration";

type Page = "jobs" | "companies" | "add-company";

const emptyEmployer = {
  name: "",
  website_url: "",
  organization_type: "unresolved",
  city: "Cape Town",
  province: "Western Cape",
  country: "South Africa",
};

export default function App() {
  const [page, setPage] = useState<Page>("jobs");
  const [showArchived, setShowArchived] = useState(false);
  const [reviewFilter, setReviewFilter] = useState("all");
  const [logoUrl, setLogoUrl] = useState("");
  const [logoSourceUrl, setLogoSourceUrl] = useState("");
  const [companyQuery, setCompanyQuery] = useState("");
  const [companyStatusFilter, setCompanyStatusFilter] = useState("all");
  const [selectedEmployerId, setSelectedEmployerId] = useState("all");
  const [sources, setSources] = useState<EmployerSource[]>([]);
  const [form, setForm] = useState(emptyEmployer);
  const [sourceUrl, setSourceUrl] = useState("");
  const [editingSourceId, setEditingSourceId] = useState<string | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
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

  const visibleEmployers = employers.filter(
    (item) =>
      item.name.toLowerCase().includes(companyQuery.toLowerCase()) &&
      (companyStatusFilter === "all" || item.status === companyStatusFilter),
  );
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

  return (
    <main className="mx-auto flex h-screen max-w-[1600px] flex-col overflow-hidden px-4 pb-3 pt-4 md:px-8">
      <AppShellHeader
        activePage={page}
        onSelectPage={setPage}
        onRefresh={() => void loadWorkspace()}
        refreshing={loading}
      />

      <OperationalAlerts error={error} notice={notice} />

      {page === "jobs" && (
        <section className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
          <div className="flex items-center justify-between gap-3">
            <span className="text-[10px] font-medium text-muted-foreground/70">
              {loading ? "Refreshing data…" : "Updated from Scout records"}
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="h-8 bg-card"
                onClick={() => void loadWorkspace()}
                disabled={loading || extracting}
              >
                <RefreshCw className={`mr-1 h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
                Refresh
              </Button>
              <Button
                size="sm"
                className="h-8 bg-[var(--scout-cyan)] text-primary hover:opacity-90"
                onClick={() => void fetchJobs()}
                disabled={loading || extracting}
              >
                <BriefcaseBusiness className="mr-1 h-3.5 w-3.5" />
                {extracting ? "Fetching jobs…" : "Fetch jobs"}
              </Button>
            </div>
          </div>
          <DashboardOverview
            vacancyCount={vacancies.length}
            employerCount={employers.length}
            newVacancies24h={newVacancies24h}
            attentionCount={attentionCount}
            atsPerformance={atsPerformance}
          />
          <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
            <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
              <VacancyRecordsToolbar
                showArchived={showArchived}
                onShowArchivedChange={(show) => {
                  setShowArchived(show);
                  clearSelection();
                }}
                reviewFilter={reviewFilter}
                onReviewFilterChange={setReviewFilter}
                selectedEmployerId={selectedEmployerId}
                onEmployerChange={setSelectedEmployerId}
                employers={employers}
                onRefresh={() => void loadWorkspace()}
                loading={loading}
              />
              <VacancyRecordList
                vacancies={filteredVacancies}
                loading={loading}
                selectedVacancyId={selectedVacancyId}
                openingVacancyId={openingVacancyId}
                onOpenVacancy={(vacancyId) => void openVacancy(vacancyId, visibleVacancies)}
              />
            </section>
            <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
              <VacancyDetailsPanel
                vacancy={selectedVacancy}
                loading={Boolean(openingVacancyId)}
                reviewReason={reviewReason}
                saving={vacancySaving}
                onChangeReviewReason={setReviewReason}
                onClear={clearSelection}
                onDecision={(status) => void setVacancyDecision(status)}
                onArchive={() => void archiveSelectedVacancy()}
                onRestore={() => void restoreSelectedVacancy()}
              />
            </section>
          </div>
        </section>
      )}

      {page === "companies" && (
        <>
          <p className="mb-3 text-xs text-muted-foreground">
            Manage company identity, verification, branding and registered ATS sources.
          </p>
          <CompanyAttentionActions
            employers={employers}
            sources={dashboardSources}
            onSelectCompany={(employer) => void openCompany(employer)}
          />
          <div className="grid min-h-0 gap-3 lg:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.5fr)]">
            <section className="min-w-0 rounded-xl border border-border bg-card p-4 shadow-sm">
              <div className="mb-3 flex items-center justify-between gap-3 border-b border-border pb-3">
                <div className="flex items-center gap-3">
                  <h3>Registered companies</h3>
                  <span>
                    {visibleEmployers.length} / {employers.length}
                  </span>
                </div>
                <Button
                  type="button"
                  className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
                  onClick={() => {
                    setPage("add-company");
                    setError("");
                    setNotice("");
                  }}
                >
                  + Add company
                </Button>
              </div>
              <CompanySearchFilters
                searchQuery={companyQuery}
                onSearchChange={setCompanyQuery}
                statusFilter={companyStatusFilter}
                onStatusFilterChange={setCompanyStatusFilter}
              />
              <CompanyDirectoryList
                employers={visibleEmployers}
                selectedEmployerId={selectedEmployerId}
                onSelectEmployer={(employer) => void openCompany(employer)}
                emptyMessage={
                  employers.length
                    ? "No companies match these filters."
                    : "No companies registered."
                }
              />
            </section>
            <section className="min-w-0 rounded-xl border border-border bg-card p-4 shadow-sm">
              {selectedEmployer ? (
                <>
                  <CompanyProfileHeader
                    employer={selectedEmployer}
                    jobsCount={
                      vacancies.filter((item) => item.employer_id === selectedEmployer.id).length
                    }
                    sourcesCount={sources.length}
                  />
                  <CompanyProfileActions
                    currentStatus={selectedEmployer.status}
                    saving={saving}
                    onUpdateStatus={(status) => void updateCompanyStatus(status)}
                    onDelete={() => void deleteCompany()}
                  />
                  <CompanyBrandingForm
                    logoUrl={logoUrl}
                    logoSourceUrl={logoSourceUrl}
                    saving={saving}
                    onLogoUrlChange={setLogoUrl}
                    onLogoSourceUrlChange={setLogoSourceUrl}
                    onSubmit={saveEmployerBranding}
                  />
                  <CompanySourcesSection
                    sources={sources}
                    extractionRuns={extractionRuns}
                    decisions={sourceDecision}
                    sourceUrl={sourceUrl}
                    editingSourceId={editingSourceId}
                    inspection={inspection}
                    saving={saving}
                    inspecting={inspecting}
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
                </>
              ) : (
                <div className="grid min-h-[260px] content-center gap-2 px-6 text-center text-sm text-muted-foreground">
                  <strong>Select a company</strong>
                  <span>Choose a company to view its profile and registered job sources.</span>
                </div>
              )}
            </section>
          </div>
        </>
      )}

      {page === "add-company" && (
        <>
          <p className="mb-3 text-xs text-muted-foreground">
            Register a company and connect its official careers source.
          </p>
          <section className="w-full max-w-2xl rounded-xl border border-border bg-card p-4 shadow-sm sm:p-6">
            <form
              className="grid gap-4"
              onSubmit={
                discovery
                  ? registerDiscoveredEmployer
                  : (event) => {
                      event.preventDefault();
                      void discover(sourceUrl, (detectedName) =>
                        setForm((current) => ({
                          ...current,
                          name: current.name || detectedName,
                          website_url: sourceUrl,
                        })),
                      );
                    }
              }
            >
              <OnboardingUrlForm
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
                onDetect={() =>
                  void discover(sourceUrl, (detectedName) =>
                    setForm((current) => ({
                      ...current,
                      name: current.name || detectedName,
                      website_url: sourceUrl,
                    })),
                  )
                }
                inspecting={inspecting}
              />
              <OnboardingPreviewCard discovery={discovery} />
              {discovery && (
                <label>
                  Company name
                  <Input
                    value={form.name}
                    onChange={(event) => setForm({ ...form, name: event.target.value })}
                    placeholder="Detected company name"
                    required
                  />
                </label>
              )}
              <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border pt-3">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setPage("companies");
                    setDiscovery(null);
                  }}
                >
                  Cancel
                </Button>
                {discovery && (
                  <Button
                    type="submit"
                    size="sm"
                    disabled={
                      saving ||
                      !discovery.complete ||
                      !["success", "empty"].includes(discovery.outcome)
                    }
                  >
                    {saving ? "Registering and retrieving…" : "Confirm & register"}
                  </Button>
                )}
              </div>
            </form>
          </section>
        </>
      )}

      <footer className="mt-5 border-t pt-3 text-[10px] text-muted-foreground">
        Scout is a private operations workspace. Only verified, quality-checked records are eligible
        for publishing to Thungatha.
      </footer>
    </main>
  );
}
