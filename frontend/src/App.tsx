import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  BriefcaseBusiness,
  Building2,
  CircleAlert,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import type { FormEvent } from "react";
import { scoutApi } from "./api";
import type {
  Employer,
  EmployerSource,
  ExtractionRun,
  GreenhouseInspection,
  CareersDiscovery,
  Vacancy,
} from "./api";
import { Badge } from "@/components/ui/badge";
import { AppShellHeader } from "./app-shell/AppShellHeader";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { decodeGreenhouseContent } from "./job-management/html-content-decoder";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CompanyProfileActions } from "./company-management/CompanyProfileActions";
import { CompanyDirectoryList } from "./company-management/CompanyDirectoryList";
import { CompanySearchFilters } from "./company-management/CompanySearchFilters";
import { CompanyProfileHeader } from "./company-management/CompanyProfileHeader";
import { SourceReviewPanel } from "./employer-sources/SourceReviewPanel";
import { ExtractionRunHistory } from "./employer-sources/ExtractionRunHistory";
import { SourceRegistrationForm } from "./employer-sources/SourceRegistrationForm";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Page = "jobs" | "companies" | "add-company";

const emptyEmployer = {
  name: "",
  website_url: "",
  organization_type: "unresolved",
  city: "Cape Town",
  province: "Western Cape",
  country: "South Africa",
};

const reviewLabel = (status: Vacancy["review_status"]) =>
  ({
    pending: "Pending review",
    needs_verification: "Needs verification",
    verified: "Verified",
    rejected: "Rejected",
  })[status];

export default function App() {
  const [page, setPage] = useState<Page>("jobs");
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [archivedVacancies, setArchivedVacancies] = useState<Vacancy[]>([]);
  const [showArchived, setShowArchived] = useState(false);
  const [reviewFilter, setReviewFilter] = useState("all");
  const [selectedVacancy, setSelectedVacancy] = useState<Vacancy | null>(null);
  const [selectedVacancyId, setSelectedVacancyId] = useState<string | null>(null);
  const [openingVacancyId, setOpeningVacancyId] = useState<string | null>(null);
  const vacancyRequestRef = useRef(0);
  const [reviewReason, setReviewReason] = useState("");
  const [logoUrl, setLogoUrl] = useState("");
  const [logoSourceUrl, setLogoSourceUrl] = useState("");
  const [sourceDecision, setSourceDecision] = useState<
    Record<
      string,
      { status: string; permission_status: string; evidence_url: string; reason: string }
    >
  >({});
  const [companyQuery, setCompanyQuery] = useState("");
  const [companyStatusFilter, setCompanyStatusFilter] = useState("all");
  const [vacancySaving, setVacancySaving] = useState(false);
  const [selectedEmployerId, setSelectedEmployerId] = useState("all");
  const [sources, setSources] = useState<EmployerSource[]>([]);
  const [dashboardSources, setDashboardSources] = useState<EmployerSource[]>([]);
  const [extractionRuns, setExtractionRuns] = useState<Record<string, ExtractionRun[]>>({});
  const [form, setForm] = useState(emptyEmployer);
  const [sourceUrl, setSourceUrl] = useState("");
  const [editingSourceId, setEditingSourceId] = useState<string | null>(null);
  const [inspection, setInspection] = useState<GreenhouseInspection | null>(null);
  const [discovery, setDiscovery] = useState<CareersDiscovery | null>(null);
  const [atsKey, setAtsKey] = useState("greenhouse");
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [inspecting, setInspecting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const selectedEmployer = employers.find((item) => item.id === selectedEmployerId) ?? null;
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

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextEmployers, nextVacancies, nextArchived] = await Promise.all([
        scoutApi.listEmployers(),
        scoutApi.listVacancies(),
        scoutApi.listArchivedVacancies(),
      ]);
      setEmployers(nextEmployers);
      setVacancies(nextVacancies);
      setArchivedVacancies(nextArchived);
      const sourceGroups = await Promise.all(
        nextEmployers.map(async (employer) => ({
          employer,
          sources: await scoutApi.listSources(employer.id),
        })),
      );
      const allSources = sourceGroups.flatMap((group) => group.sources);
      setDashboardSources(allSources);
      const runEntries = await Promise.all(
        allSources.map(
          async (source) => [source.id, await scoutApi.listExtractionRuns(source.id)] as const,
        ),
      );
      setExtractionRuns(Object.fromEntries(runEntries));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

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

  async function updateSourceDecision(source: EmployerSource) {
    const decision = sourceDecision[source.id] ?? {
      status: source.status,
      permission_status: source.permission_status,
      evidence_url: "",
      reason: "",
    };
    if (
      decision.status === "verified" &&
      decision.permission_status === "allowed" &&
      !decision.evidence_url.trim()
    ) {
      setError("Add an evidence URL before verifying and permitting this source.");
      return;
    }
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const updated = await scoutApi.updateSourceReview(selectedEmployer!.id, source.id, decision);
      setSources((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setDashboardSources((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
      setNotice("Source verification and permission decision saved.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update source decision.");
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

  async function openVacancy(vacancyId: string) {
    const requestId = ++vacancyRequestRef.current;
    setError("");
    setSelectedVacancyId(vacancyId);
    setOpeningVacancyId(vacancyId);
    setSelectedVacancy(null);
    try {
      const vacancy = await scoutApi.getVacancy(vacancyId);
      if (requestId !== vacancyRequestRef.current) return;
      const listRecord = visibleVacancies.find((item) => item.id === vacancyId);
      const completeVacancy = {
        ...vacancy,
        description: vacancy.description ?? listRecord?.description ?? null,
      };
      setSelectedVacancy(completeVacancy);
      setReviewReason(completeVacancy.review_reason ?? "");
    } catch (reason) {
      if (requestId !== vacancyRequestRef.current) return;
      setError(reason instanceof Error ? reason.message : "Could not load vacancy details.");
      setSelectedVacancyId(null);
    } finally {
      if (requestId === vacancyRequestRef.current) setOpeningVacancyId(null);
    }
  }

  async function setVacancyDecision(status: Vacancy["review_status"]) {
    if (!selectedVacancy) return;
    setVacancySaving(true);
    setError("");
    try {
      const updated = await scoutApi.updateVacancyReview(selectedVacancy.id, status, reviewReason);
      setSelectedVacancy(updated);
      setVacancies((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setNotice(`Vacancy marked ${status.replaceAll("_", " ")}.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not save the vacancy decision.");
    } finally {
      setVacancySaving(false);
    }
  }

  async function archiveSelectedVacancy() {
    if (!selectedVacancy) return;
    const reason = window.prompt("Why are you archiving this vacancy?") ?? "";
    if (!reason.trim()) return;
    setVacancySaving(true);
    setError("");
    try {
      await scoutApi.archiveVacancy(selectedVacancy.id, reason);
      setSelectedVacancy(null);
      await loadWorkspace();
      setNotice("Vacancy archived. It remains available in the Archived jobs view.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not archive vacancy.");
    } finally {
      setVacancySaving(false);
    }
  }

  async function restoreSelectedVacancy() {
    if (!selectedVacancy) return;
    setVacancySaving(true);
    setError("");
    try {
      await scoutApi.restoreVacancy(selectedVacancy.id);
      setSelectedVacancy(null);
      await loadWorkspace();
      setNotice("Vacancy restored to the active jobs list.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not restore vacancy.");
    } finally {
      setVacancySaving(false);
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
              <div className="flex flex-wrap items-center gap-2 border-b border-border bg-muted/70 p-3">
                <h3 className="mr-auto text-sm font-bold text-primary">
                  {showArchived ? "Archived vacancies" : "Vacancy records"}
                </h3>
                <Select
                  value={showArchived ? "archived" : "active"}
                  onValueChange={(value) => {
                    setShowArchived(value === "archived");
                    setSelectedVacancy(null);
                    setSelectedVacancyId(null);
                  }}
                >
                  <SelectTrigger className="h-8 w-[125px] bg-card text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active records</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={reviewFilter} onValueChange={setReviewFilter}>
                  <SelectTrigger className="h-8 w-[145px] bg-card text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All review states</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="needs_verification">Needs verification</SelectItem>
                    <SelectItem value="verified">Verified</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={selectedEmployerId} onValueChange={setSelectedEmployerId}>
                  <SelectTrigger className="h-8 w-[140px] bg-card text-xs">
                    <SelectValue placeholder="All companies" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All companies</SelectItem>
                    {employers.map((employer) => (
                      <SelectItem key={employer.id} value={employer.id}>
                        {employer.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 bg-card"
                  onClick={() => void loadWorkspace()}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </div>
              <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
                {loading ? (
                  <p className="py-12 text-center text-sm text-muted-foreground">
                    Loading operational data…
                  </p>
                ) : filteredVacancies.length === 0 ? (
                  <div className="py-12 text-center">
                    <p className="text-sm font-semibold">No matching records</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Adjust the filters or register a source.
                    </p>
                  </div>
                ) : (
                  filteredVacancies.map((vacancy) => (
                    <button
                      key={vacancy.id}
                      type="button"
                      onClick={() => void openVacancy(vacancy.id)}
                      aria-pressed={selectedVacancyId === vacancy.id}
                      className={`w-full rounded-lg border p-3 text-left shadow-sm transition-all hover:border-ring hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${selectedVacancyId === vacancy.id ? "border-ring bg-accent shadow-sm" : "border-border bg-card"}`}
                    >
                      <span className="flex items-start justify-between gap-3">
                        <strong className="text-sm font-semibold leading-snug text-primary">
                          {vacancy.title}
                        </strong>
                        <Badge
                          variant={
                            vacancy.review_status === "verified"
                              ? "default"
                              : vacancy.review_status === "rejected"
                                ? "destructive"
                                : "secondary"
                          }
                          className={
                            vacancy.review_status === "pending"
                              ? "bg-[var(--warning-surface)] text-[var(--warning-text)] hover:bg-[var(--warning-surface)]"
                              : vacancy.review_status === "needs_verification"
                                ? "bg-[var(--warning-surface)] text-[var(--warning-text)] hover:bg-[var(--warning-surface)]"
                                : ""
                          }
                        >
                          {reviewLabel(vacancy.review_status)}
                        </Badge>
                      </span>
                      <span className="mt-1 block text-xs font-medium text-muted-foreground">
                        {vacancy.employer_name}
                      </span>
                      <span className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-muted-foreground">
                        <span>{vacancy.location_text || "Location unknown"}</span>
                        {vacancy.department && <span>{vacancy.department}</span>}
                        <span>
                          First seen{" "}
                          {new Date(
                            vacancy.first_seen_at ?? vacancy.last_seen_at,
                          ).toLocaleDateString()}
                        </span>
                      </span>
                    </button>
                  ))
                )}
              </div>
            </section>
            <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
              {openingVacancyId ? (
                <div className="grid flex-1 place-content-center text-center text-sm text-muted-foreground">
                  Loading vacancy…
                </div>
              ) : selectedVacancy ? (
                <>
                  <div className="flex items-center justify-between gap-3 border-b border-border bg-primary p-4 text-primary-foreground">
                    <div className="min-w-0">
                      <p className="text-[10px] font-medium text-[var(--scout-cyan)]">
                        {selectedVacancy.employer_name} ·{" "}
                        {selectedVacancy.location_text || "Location unknown"}
                      </p>
                      <h3 className="mt-1 text-sm font-bold">{selectedVacancy.title}</h3>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-primary-foreground/75 hover:bg-card/10 hover:text-white"
                      onClick={() => {
                        setSelectedVacancy(null);
                        setSelectedVacancyId(null);
                      }}
                    >
                      Clear
                    </Button>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-3">
                    <Button
                      asChild
                      size="sm"
                      className="bg-[var(--scout-cyan)] text-primary hover:opacity-90"
                    >
                      <a href={selectedVacancy.application_url} target="_blank" rel="noreferrer">
                        Open source listing ↗
                      </a>
                    </Button>
                    <Button asChild size="sm" variant="outline">
                      <a href={selectedVacancy.source_url} target="_blank" rel="noreferrer">
                        Source record ↗
                      </a>
                    </Button>
                    <Badge className="bg-[var(--warning-surface)] text-[var(--warning-text)]">
                      {reviewLabel(selectedVacancy.review_status)}
                    </Badge>
                  </div>
                  <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
                    <div>
                      <h4 className="mb-2 text-sm font-bold text-primary">Extracted description</h4>
                      {selectedVacancy.description ? (
                        <iframe
                          className="h-[min(42vh,500px)] min-h-[280px] w-full rounded-lg border border-border bg-card"
                          title={"Description for " + selectedVacancy.title}
                          sandbox=""
                          srcDoc={
                            '<!doctype html><html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src https: data:; style-src \'unsafe-inline\';"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{font:14px/1.65 system-ui,sans-serif;color:#263449;margin:18px;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:#168bb9}img{max-width:100%;height:auto}ul,ol{padding-left:24px}</style></head><body>' +
                            decodeGreenhouseContent(selectedVacancy.description) +
                            "</body></html>"
                          }
                        />
                      ) : (
                        <p className="rounded-lg bg-[var(--warning-surface)] p-4 text-sm text-[var(--warning-text)]">
                          No description was saved by the source. Inspect the source listing.
                        </p>
                      )}
                    </div>
                    <section className="rounded-lg border border-border">
                      <div className="border-b bg-muted px-3 py-2">
                        <h4 className="text-xs font-bold text-primary">Admin review actions</h4>
                        <p className="mt-1 text-[10px] text-muted-foreground">
                          Pending is the database default; it does not mean automated verification
                          has run.
                        </p>
                      </div>
                      <div className="space-y-3 p-3">
                        <label className="grid gap-1 text-xs font-medium text-muted-foreground">
                          Decision notes
                          <input
                            className="h-9 rounded-md border border-border bg-card px-3 text-sm font-normal"
                            value={reviewReason}
                            disabled={Boolean(selectedVacancy.archived_at)}
                            onChange={(event) => setReviewReason(event.target.value)}
                            placeholder="Record the reason for your decision"
                          />
                        </label>
                        <div className="flex flex-wrap gap-2">
                          <Button
                            size="sm"
                            disabled={vacancySaving || Boolean(selectedVacancy.archived_at)}
                            onClick={() => void setVacancyDecision("verified")}
                            className="bg-[var(--success-text)] text-white hover:brightness-95"
                          >
                            <ShieldCheck className="h-4 w-4" />
                            Mark verified
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={vacancySaving || Boolean(selectedVacancy.archived_at)}
                            onClick={() => void setVacancyDecision("needs_verification")}
                          >
                            Needs verification
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            disabled={vacancySaving || Boolean(selectedVacancy.archived_at)}
                            onClick={() => void setVacancyDecision("rejected")}
                          >
                            Reject record
                          </Button>
                          {selectedVacancy.archived_at ? (
                            <Button size="sm" onClick={() => void restoreSelectedVacancy()}>
                              Restore
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => void archiveSelectedVacancy()}
                            >
                              Archive
                            </Button>
                          )}
                        </div>
                      </div>
                    </section>
                    <details className="rounded-lg border border-border">
                      <summary className="cursor-pointer px-3 py-2 text-xs font-semibold text-muted-foreground">
                        Publishing payload preview
                      </summary>
                      <pre className="max-h-64 overflow-auto border-t bg-muted p-3 text-xs">
                        {JSON.stringify(
                          {
                            title: selectedVacancy.title,
                            company: selectedVacancy.employer_name,
                            location: selectedVacancy.location_text,
                            review_status: selectedVacancy.review_status,
                            review_reason: selectedVacancy.review_reason,
                            application_url: selectedVacancy.application_url,
                            source_url: selectedVacancy.source_url,
                          },
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  </div>
                </>
              ) : (
                <div className="grid flex-1 place-content-center px-6 text-center">
                  <p className="text-sm font-semibold text-primary">Select a vacancy record</p>
                  <p className="mt-1 max-w-xs text-xs text-muted-foreground">
                    Inspect extracted content and resolve records requiring admin attention.
                  </p>
                </div>
              )}
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
              <CompanyProfileHeader
                    employer={selectedEmployer}
                    jobsCount={vacancies.filter((item) => item.employer_id === selectedEmployer.id).length}
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
                              setSourceDecision((current) => {
                                const existing = current[source.id] ?? {
                                  status: source.status,
                                  permission_status: source.permission_status,
                                  evidence_url: "",
                                  reason: "",
                                };
                                return {
                                  ...current,
                                  [source.id]: { ...existing, [field]: value },
                                };
                              })
                            }
                            onSave={() => void updateSourceDecision(source)}
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
              <label>
                Careers / jobs listing URL
                <input
                  type="url"
                  value={sourceUrl}
                  onChange={(event) => {
                    setSourceUrl(event.target.value);
                    setDiscovery(null);
                    setForm({ ...form, website_url: event.target.value });
                  }}
                  placeholder="https://company.com/jobs"
                  required
                />
              </label>
              <label>
                ATS platform
                <select
                  value={atsKey}
                  onChange={(event) => {
                    setAtsKey(event.target.value);
                    setDiscovery(null);
                  }}
                >
                  <option value="greenhouse">Greenhouse</option>
                  <option value="workday" disabled>
                    Workday — coming next
                  </option>
                </select>
              </label>
              <button
                type="button"
                className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
                onClick={() => void discoverCareersPage()}
                disabled={inspecting || !sourceUrl.trim()}
              >
                {inspecting ? "Detecting ATS and inspecting jobs…" : "Detect ATS & preview jobs"}
              </button>
              {discovery && (
                <div className="grid gap-2 rounded-lg border border-border bg-muted/50 p-3 text-xs">
                  <strong>{discovery.jobs.length} vacancies found</strong>
                  <span>
                    Detected: {discovery.detected_adapter} · Board: {discovery.board_url}
                  </span>
                  <small>
                    {discovery.complete
                      ? "Vacancy preview is complete."
                      : discovery.detail || "The preview is incomplete."}
                  </small>
                </div>
              )}
              {discovery && (
                <label>
                  Company name
                  <input
                    value={form.name}
                    onChange={(event) => setForm({ ...form, name: event.target.value })}
                    placeholder="Detected company name"
                    required
                  />
                </label>
              )}
              <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border pt-3">
                <button
                  type="button"
                  className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground disabled:pointer-events-none disabled:opacity-50"
                  onClick={() => {
                    setPage("companies");
                    setDiscovery(null);
                  }}
                >
                  Cancel
                </button>
                {discovery && (
                  <button
                    className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
                    disabled={
                      saving ||
                      !discovery.complete ||
                      !["success", "empty"].includes(discovery.outcome)
                    }
                  >
                    {saving ? "Registering and retrieving…" : "Confirm & register"}
                  </button>
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
