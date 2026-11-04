import { useMemo, useState } from "react";
import {
  Activity,
  BriefcaseBusiness,
  Building2,
  CircleAlert,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import type { FormEvent } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, GreenhouseInspection, CareersDiscovery } from "./api";
import { Badge } from "@/components/ui/badge";
import { AppShellHeader } from "./app-shell/AppShellHeader";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CompanyProfileActions } from "./company-management/CompanyProfileActions";
import { CompanyDirectoryList } from "./company-management/CompanyDirectoryList";
import { CompanySearchFilters } from "./company-management/CompanySearchFilters";
import { CompanyProfileHeader } from "./company-management/CompanyProfileHeader";
import { SourceReviewPanel } from "./employer-sources/SourceReviewPanel";
import { ExtractionRunHistory } from "./employer-sources/ExtractionRunHistory";
import { SourceRegistrationForm } from "./employer-sources/SourceRegistrationForm";
import { useEmployerSourceReview } from "./employer-sources/useEmployerSourceReview";
import { VacancyDetailsPanel } from "./job-management/VacancyDetailsPanel";
import { VacancyRecordList } from "./job-management/VacancyRecordList";
import { VacancyRecordsToolbar } from "./job-management/VacancyRecordsToolbar";
import { useVacancyReview } from "./job-management/useVacancyReview";
import { OnboardingUrlForm } from "./employer-onboarding/OnboardingUrlForm";
import { OnboardingPreviewCard } from "./employer-onboarding/OnboardingPreviewCard";
import { useScoutWorkspace } from "./useScoutWorkspace";

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
  const [inspection, setInspection] = useState<GreenhouseInspection | null>(null);
  const [discovery, setDiscovery] = useState<CareersDiscovery | null>(null);
  const [atsKey, setAtsKey] = useState("greenhouse");
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [inspecting, setInspecting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

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
  const visibleEmployers = employers.filter(
    (item) =>
      item.name.toLowerCase().includes(companyQuery.toLowerCase()) &&
      (companyStatusFilter === "all" || item.status === companyStatusFilter),
  );
  const visibleVacancies = showArchived ? archivedVacancies : vacancies;
  const newVacancies24h = vacancies.filter(
    (item) => item.first_seen_at && Date.now() - new Date(item.first_seen_at).getTime() < 86400000,
  ).length;
  const attentionCount = vacancies.filter(
    (item) => item.review_status === "pending" || item.review_status === "needs_verification",
  ).length;
  const atsPerformance = useMemo(
    () =>
      Array.from(
        new Set(["greenhouse", ...dashboardSources.map((source) => source.adapter_key)]),
      ).map((adapter) => {
        const adapterSources = dashboardSources.filter((source) => source.adapter_key === adapter);
        const runs = adapterSources.flatMap((source) => extractionRuns[source.id] ?? []);
        const latest = runs.sort(
          (a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
        )[0];
        return {
          adapter,
          sourceCount: adapterSources.length,
          verified: adapterSources.filter(
            (source) => source.status === "verified" && source.permission_status === "allowed",
          ).length,
          jobCount: vacancies.filter((job) =>
            adapterSources.some((source) => source.id === job.source_id),
          ).length,
          latest,
          failed: runs.filter((run) => !["success", "empty"].includes(run.outcome)).length,
        };
      }),
    [dashboardSources, extractionRuns, vacancies],
  );
  const filteredVacancies = useMemo(
    () =>
      selectedEmployerId === "all"
        ? visibleVacancies
        : visibleVacancies.filter((item) => item.employer_id === selectedEmployerId),
    [visibleVacancies, selectedEmployerId],
  ).filter((item) => reviewFilter === "all" || item.review_status === reviewFilter);

  async function fetchJobs() {
    const eligibleSources = dashboardSources.filter(
      (source) => source.status === "verified" && source.permission_status === "allowed",
    );
    if (!eligibleSources.length) {
      setError(
        "No job sources are both verified and permitted. Review company sources before fetching jobs.",
      );
      return;
    }

    setExtracting(true);
    setError("");
    setNotice("");
    const results = await Promise.allSettled(
      eligibleSources.map((source) => scoutApi.extractSource(source.id)),
    );
    const succeeded = results.filter((result) => result.status === "fulfilled").length;
    const failed = results.length - succeeded;
    await loadWorkspace();
    setNotice(
      failed
        ? `Fetched from ${succeeded} source(s); ${failed} source(s) failed. Check the extraction history.`
        : `Fetch completed for ${succeeded} verified source(s). Dashboard data has been refreshed.`,
    );
    setExtracting(false);
  }

  async function openCompany(employer: Employer) {
    setEditingSourceId(null);
    setSourceUrl("");
    setInspection(null);
    setSelectedEmployerId(employer.id);
    setLogoUrl(employer.logo_url ?? "");
    setLogoSourceUrl(employer.logo_source_url ?? "");
    setPage("companies");
    setError("");
    try {
      const nextSources = await scoutApi.listSources(employer.id);
      setSources(nextSources);
      const runEntries = await Promise.all(
        nextSources.map(
          async (source) => [source.id, await scoutApi.listExtractionRuns(source.id)] as const,
        ),
      );
      setExtractionRuns((current) => ({
        ...current,
        ...Object.fromEntries(runEntries),
      }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load company sources.");
    }
  }

  async function updateCompanyStatus(
    status: "approved" | "needs_review" | "rejected" | "inactive",
  ) {
    if (!selectedEmployer) return;
    setSaving(true);
    setError("");
    try {
      const updated = await scoutApi.updateEmployerStatus(selectedEmployer.id, status);
      setEmployers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setNotice(`${updated.name} marked ${status.replaceAll("_", " ")}.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update company status.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteCompany() {
    if (!selectedEmployer) return;
    if (
      !window.confirm(
        `Permanently delete ${selectedEmployer.name}? Companies with sources or vacancies cannot be deleted.`,
      )
    )
      return;
    setSaving(true);
    setError("");
    try {
      await scoutApi.deleteEmployer(selectedEmployer.id);
      setEmployers((current) => current.filter((item) => item.id !== selectedEmployer.id));
      setSelectedEmployerId("all");
      setSources([]);
      setNotice("Company deleted.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not delete company.");
    } finally {
      setSaving(false);
    }
  }

  async function saveEmployerBranding(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedEmployer) return;
    setSaving(true);
    setError("");
    try {
      const updated = await scoutApi.updateEmployerBranding(
        selectedEmployer.id,
        logoUrl.trim(),
        logoSourceUrl.trim(),
      );
      setEmployers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setNotice("Company logo details saved.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save company logo details.");
    } finally {
      setSaving(false);
    }
  }

  async function discoverCareersPage() {
    setInspecting(true);
    setError("");
    setNotice("");
    setDiscovery(null);
    try {
      if (atsKey !== "greenhouse") {
        throw new Error("Workday discovery will be enabled in the Workday vertical slice.");
      }
      const result = await scoutApi.discoverCareersPage(sourceUrl);
      setDiscovery(result);
      setForm((current) => ({
        ...current,
        name: current.name || result.company_name || "",
        website_url: sourceUrl,
      }));
      setNotice(`Detected ${result.detected_adapter} and found ${result.jobs.length} vacancies.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not discover the careers source.");
    } finally {
      setInspecting(false);
    }
  }

  async function registerDiscoveredEmployer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!discovery || !form.name.trim()) return;
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const created = await scoutApi.createEmployer({
        ...form,
        website_url: sourceUrl,
      });
      const source = await scoutApi.createSource(created.id, {
        adapter_key: discovery.detected_adapter,
        source_url: discovery.board_url,
        normalized_url: discovery.board_url,
        employer_careers_url: sourceUrl,
        adapter_config: { slug: discovery.board_token },
      });
      const run = await scoutApi.extractSource(source.id);
      await loadWorkspace();
      setSelectedEmployerId(created.id);
      setSources([source]);
      setExtractionRuns((current) => ({ ...current, [source.id]: [run] }));
      setPage("companies");
      setSourceUrl("");
      setDiscovery(null);
      setForm(emptyEmployer);
      setNotice(
        `${created.name} registered. ${run.jobs_received} vacancies retrieved; ${run.outcome}.`,
      );
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Could not register employer and source.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function inspectGreenhouse() {
    setInspecting(true);
    setError("");
    setInspection(null);
    try {
      setInspection(await scoutApi.inspectGreenhouse(sourceUrl));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not inspect Greenhouse board.");
    } finally {
      setInspecting(false);
    }
  }

  async function createSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedEmployer) return;
    setSaving(true);
    setError("");
    try {
      const payload = {
        adapter_key: editingSourceId
          ? sources.find((source) => source.id === editingSourceId)?.adapter_key
          : "greenhouse",
        source_url: sourceUrl,
        normalized_url: sourceUrl,
        adapter_config: { slug: inspection?.board_token },
      };
      if (editingSourceId) {
        await scoutApi.updateSource(selectedEmployer.id, editingSourceId, payload);
        setSources(await scoutApi.listSources(selectedEmployer.id));
        setNotice(
          "Source configuration updated. Its verification and permission states were preserved.",
        );
      } else {
        const created = await scoutApi.createSource(selectedEmployer.id, {
          ...payload,
          employer_careers_url: selectedEmployer.website_url ?? null,
        });
        setSources((current) => [...current, created]);
        setNotice("Greenhouse source registered. Verification and permission remain pending.");
      }
      setEditingSourceId(null);
      setSourceUrl("");
      setInspection(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not register source.");
    } finally {
      setSaving(false);
    }
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
          <div className="grid grid-cols-2 gap-2 xl:grid-cols-4">
            {[
              {
                label: "Collected vacancies",
                value: vacancies.length,
                note: "Active records",
                icon: BriefcaseBusiness,
                color: "text-accent-foreground",
                bg: "bg-accent",
              },
              {
                label: "Registered companies",
                value: employers.length,
                note: "Employer records",
                icon: Building2,
                color: "text-secondary-foreground",
                bg: "bg-secondary",
              },
              {
                label: "New in last 24 hours",
                value: newVacancies24h,
                note: "Based on first seen time",
                icon: Sparkles,
                color: "text-[var(--success-text)]",
                bg: "bg-[var(--success-surface)]",
              },
              {
                label: "Needs admin attention",
                value: attentionCount,
                note: "Pending or needs verification",
                icon: CircleAlert,
                color: "text-[var(--warning-text)]",
                bg: "bg-[var(--warning-surface)]",
              },
            ].map(({ label, value, note, icon: Icon, color, bg }) => (
              <div
                key={label}
                className="flex items-center gap-3 rounded-xl border border-border bg-card p-3 shadow-sm"
              >
                <span
                  className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${bg} ${color}`}
                >
                  <Icon className="h-5 w-5" />
                </span>
                <div className="min-w-0">
                  <p className="text-[11px] font-medium text-muted-foreground">{label}</p>
                  <p className="text-xl font-bold leading-tight text-primary">{value}</p>
                  <p className="text-[10px] text-muted-foreground/70">{note}</p>
                </div>
              </div>
            ))}
          </div>
          <section className="rounded-xl border border-border bg-card p-3 shadow-sm">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="flex items-center gap-2 text-xs font-bold text-primary">
                <Activity className="h-4 w-4 text-[var(--scout-cyan)]" /> ATS performance
              </h3>
              <span className="text-[10px] text-muted-foreground/70">
                Source health and latest extraction results
              </span>
            </div>
            <div className="grid gap-2 md:grid-cols-2">
              {atsPerformance.map((item) => (
                <div
                  key={item.adapter}
                  className="flex items-center justify-between gap-3 rounded-lg bg-muted px-3 py-2"
                >
                  <div className="min-w-0">
                    <p className="text-xs font-bold capitalize text-foreground">{item.adapter}</p>
                    <p className="text-[10px] text-muted-foreground">
                      {item.sourceCount} sources · {item.verified} verified · {item.jobCount}{" "}
                      vacancies
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge
                      variant={
                        item.latest && ["success", "empty"].includes(item.latest.outcome)
                          ? "default"
                          : item.latest && item.latest.outcome !== "running"
                            ? "destructive"
                            : "secondary"
                      }
                      className="capitalize"
                    >
                      {item.latest?.outcome ?? "No runs"}
                    </Badge>
                    <p className="mt-1 text-[10px] text-muted-foreground">
                      {item.latest
                        ? `${item.latest.jobs_inserted} new · ${item.failed} failed runs`
                        : "Awaiting first extraction"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>
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
          <section className="mb-3 grid gap-2 rounded-xl border border-border bg-card p-3 shadow-sm md:grid-cols-3">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground/70">
                Suggested actions
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Work through these records to keep the company directory and sources reliable.
              </p>
            </div>
            <Button
              type="button"
              className="rounded-lg border border-[var(--warning-text)]/15 bg-[var(--warning-surface)] px-3 py-2 text-left transition-colors hover:opacity-90"
              onClick={() => {
                const target = employers.find((item) => item.status === "discovered");
                if (target) void openCompany(target);
              }}
            >
              <strong className="block text-sm text-[var(--warning-text)]">
                {employers.filter((item) => item.status === "discovered").length} awaiting approval
              </strong>
              <span className="text-[10px] text-[var(--warning-text)]">
                Review new company records
              </span>
            </Button>
            <Button
              type="button"
              className="rounded-lg bg-[var(--warning-surface)] px-3 py-2 text-left hover:opacity-90"
              onClick={() => {
                const target = employers.find((item) => item.status === "needs_review");
                if (target) void openCompany(target);
              }}
            >
              <strong className="block text-sm text-[var(--warning-text)]">
                {employers.filter((item) => item.status === "needs_review").length} flagged for
                review
              </strong>
              <span className="text-[10px] text-[var(--warning-text)]">
                Resolve company identity concerns
              </span>
            </Button>
            <Button
              type="button"
              className="rounded-lg border border-border bg-muted px-3 py-2 text-left transition-colors hover:bg-accent"
              onClick={() => {
                const targetSource = dashboardSources.find(
                  (source) =>
                    source.status !== "verified" || source.permission_status !== "allowed",
                );
                const target =
                  targetSource && employers.find((item) => item.id === targetSource.employer_id);
                if (target) void openCompany(target);
              }}
            >
              <strong className="block text-sm text-foreground">
                {
                  dashboardSources.filter(
                    (source) =>
                      source.status !== "verified" || source.permission_status !== "allowed",
                  ).length
                }{" "}
                sources need checks
              </strong>
              <span className="text-[10px] text-muted-foreground">
                Verify source and permission status
              </span>
            </Button>
          </section>
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
                  <form
                    className="my-4 grid gap-3 rounded-lg border border-border bg-muted/50 p-4"
                    onSubmit={saveEmployerBranding}
                  >
                    <div className="flex items-center gap-3">
                      <h4>Company logo</h4>
                      <span className="text-[10px] text-muted-foreground/70">Optional</span>
                      {logoUrl && (
                        <img
                          src={logoUrl}
                          alt="Company logo preview"
                          className="h-9 w-9 rounded-md border border-border bg-card object-contain p-1"
                        />
                      )}
                    </div>
                    <label>
                      Logo image URL
                      <Input
                        type="url"
                        value={logoUrl}
                        onChange={(event) => setLogoUrl(event.target.value)}
                        placeholder="https://company.com/logo.png"
                        className="mt-1"
                      />
                    </label>
                    <p className="text-[10px] text-muted-foreground/70">
                      Scout currently accepts a logo URL and its evidence URL. A logo is not
                      required to register or approve a company.
                    </p>
                    <label>
                      Logo source / evidence URL
                      <Input
                        type="url"
                        value={logoSourceUrl}
                        onChange={(event) => setLogoSourceUrl(event.target.value)}
                        placeholder="Official company page where the logo is shown"
                        className="mt-1"
                      />
                    </label>
                    <Button type="submit" variant="outline" className="w-fit" disabled={saving}>
                      {saving ? "Saving…" : "Save logo details"}
                    </Button>
                  </form>
                  <div className="mb-3 mt-6 flex items-center justify-between gap-3 border-b border-border pb-2">
                    <h4>Job sources</h4>
                  </div>
                  {sources.length ? (
                    sources.map((source) => {
                      const runs = extractionRuns[source.id] ?? [];
                      return (
                        <div className="space-y-3 border-b border-border py-4" key={source.id}>
                          <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-card p-3">
                            <div>
                              <strong className="text-xs font-semibold capitalize text-foreground">
                                {source.adapter_key}
                              </strong>
                              <small className="block break-all text-[10px] text-muted-foreground">
                                {source.source_url}
                              </small>
                            </div>
                            <Badge variant="outline" className="capitalize">
                              {source.status.replaceAll("_", " ")}
                            </Badge>
                            {source.adapter_key === "greenhouse" && (
                              <Button
                                type="button"
                                className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
                                onClick={() => {
                                  setEditingSourceId(source.id);
                                  setSourceUrl(source.source_url);
                                  setInspection(null);
                                }}
                              >
                                Edit source
                              </Button>
                            )}
                          </div>
                          <SourceReviewPanel
                            source={source}
                            decision={sourceDecision[source.id]}
                            saving={saving}
                            onChange={(field, value) =>
                              updateSourceDecisionField(source, field, value)
                            }
                            onSave={() => void saveSourceDecision(source)}
                          />
                          <ExtractionRunHistory runs={runs} />
                        </div>
                      );
                    })
                  ) : (
                    <p className="py-4 text-xs text-muted-foreground">
                      No job source registered for this company.
                    </p>
                  )}
                  <SourceRegistrationForm
                    editingSourceId={editingSourceId}
                    sourceUrl={sourceUrl}
                    onChangeSourceUrl={(value) => {
                      setSourceUrl(value);
                      setInspection(null);
                    }}
                    onInspect={() => void inspectGreenhouse()}
                    inspection={inspection}
                    onSaveSource={createSource}
                    onCancelEdit={() => {
                      setEditingSourceId(null);
                      setSourceUrl("");
                      setInspection(null);
                    }}
                    inspecting={inspecting}
                    saving={saving}
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
                      void discoverCareersPage();
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
                onDetect={() => void discoverCareersPage()}
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

      <footer className="mt-5 border-t pt-3 text-xs text-muted-foreground">
        Scout is a private operations workspace. Only verified, quality-checked records are eligible
        for publishing to Thungatha.
      </footer>
    </main>
  );
}
