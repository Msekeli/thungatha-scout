import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Activity, BriefcaseBusiness, Building2, CircleAlert, Radar, RefreshCw, ShieldCheck, Sparkles } from "lucide-react";
import type { FormEvent } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, ExtractionRun, GreenhouseInspection, CareersDiscovery, Vacancy } from "./api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type Page = "jobs" | "companies" | "add-company";

const emptyEmployer = {
  name: "",
  website_url: "",
  organization_type: "unresolved",
  city: "Cape Town",
  province: "Western Cape",
  country: "South Africa",
};

function decodeGreenhouseContent(value: string): string {
  const decoder = document.createElement("textarea");
  let decoded = value;
  for (let pass = 0; pass < 2; pass += 1) {
    decoder.innerHTML = decoded;
    if (decoder.value === decoded) break;
    decoded = decoder.value;
  }
  return decoded;
}

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
  const [saving, setSaving] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [inspecting, setInspecting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const selectedEmployer = employers.find((item) => item.id === selectedEmployerId) ?? null;
  const visibleVacancies = showArchived ? archivedVacancies : vacancies;
  const newVacancies24h = vacancies.filter((item) => item.first_seen_at && Date.now() - new Date(item.first_seen_at).getTime() < 86400000).length;
  const attentionCount = vacancies.filter((item) => item.review_status === "pending" || item.review_status === "needs_verification").length;
  const atsPerformance = useMemo(() => ["greenhouse", "workday"].map((adapter) => {
    const adapterSources = dashboardSources.filter((source) => source.adapter_key === adapter);
    const runs = adapterSources.flatMap((source) => extractionRuns[source.id] ?? []);
    const latest = runs.sort((a, b) => new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime())[0];
    return { adapter, sourceCount: adapterSources.length, verified: adapterSources.filter((source) => source.status === "verified" && source.permission_status === "allowed").length, jobCount: vacancies.filter((job) => adapterSources.some((source) => source.id === job.source_id)).length, latest, failed: runs.filter((run) => !["success", "empty"].includes(run.outcome)).length };
  }), [dashboardSources, extractionRuns, vacancies]);
  const filteredVacancies = useMemo(
    () => selectedEmployerId === "all"
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
      const sourceGroups = await Promise.all(nextEmployers.map(async (employer) => ({ employer, sources: await scoutApi.listSources(employer.id) })));
      const allSources = sourceGroups.flatMap((group) => group.sources);
      setDashboardSources(allSources);
      const runEntries = await Promise.all(allSources.map(async (source) => [source.id, await scoutApi.listExtractionRuns(source.id)] as const));
      setExtractionRuns(Object.fromEntries(runEntries));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void loadWorkspace(); }, [loadWorkspace]);

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
        nextSources.map(async (source) => [
          source.id,
          await scoutApi.listExtractionRuns(source.id),
        ] as const),
      );
      setExtractionRuns((current) => ({
        ...current,
        ...Object.fromEntries(runEntries),
      }));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load company sources.");
    }
  }

  async function extractJobs() {
    setExtracting(true);
    setError("");
    setNotice("");
    try {
      const sourceGroups = await Promise.all(
        employers.map(async (employer) => ({
          employer: employer.name,
          sources: await scoutApi.listSources(employer.id),
        })),
      );
      const greenhouseSources = sourceGroups.flatMap((group) =>
        group.sources
          .filter((source) => source.adapter_key === "greenhouse")
          .map((source) => ({ employer: group.employer, source })),
      );
      if (greenhouseSources.length === 0) {
        setNotice("No Greenhouse sources are registered yet. Add a company and its official job source first.");
        return;
      }
      const results: Array<{ employer: string; run: ExtractionRun }> = [];
      for (const item of greenhouseSources) {
        results.push({ employer: item.employer, run: await scoutApi.extractSource(item.source.id) });
      }
      const [nextVacancies] = await Promise.all([scoutApi.listVacancies()]);
      setVacancies(nextVacancies);
      setExtractionRuns((current) => ({
        ...current,
        ...Object.fromEntries(results.map((item) => [
          item.run.source_id,
          [item.run, ...(current[item.run.source_id] ?? []).filter(
            (run) => run.id !== item.run.id,
          )].slice(0, 20),
        ])),
      }));
      const received = results.reduce((sum, item) => sum + item.run.jobs_received, 0);
      const inserted = results.reduce((sum, item) => sum + item.run.jobs_inserted, 0);
      const updated = results.reduce((sum, item) => sum + item.run.jobs_updated, 0);
      const failed = results.filter((item) => !["success", "empty"].includes(item.run.outcome));
      const summary = `Processed ${results.length} source(s): ${received} jobs received, ${inserted} new, ${updated} updated.`;
      setNotice(failed.length
        ? `${summary} ${failed.length} source(s) need attention: ${failed.map((item) => `${item.employer} — ${item.run.outcome}`).join("; ")}.`
        : summary);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not extract jobs.");
    } finally {
      setExtracting(false);
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
      setEmployers((current) => current.map((item) => item.id === updated.id ? updated : item));
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
      setVacancies((current) => current.map((item) => item.id === updated.id ? updated : item));
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
      setNotice(`${created.name} registered. ${run.jobs_received} vacancies retrieved; ${run.outcome}.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not register employer and source.");
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
        setNotice("Source configuration updated. Its verification and permission states were preserved.");
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
      <header className="flex items-center justify-between border-b pb-4">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-xl bg-[#0b1426] text-cyan-300 shadow-lg shadow-slate-900/20"><Radar className="h-6 w-6" /></span>
          <div><p className="mb-1 text-[10px] font-bold tracking-[.2em] text-slate-500">THUNGATHA / OPERATIONS</p><h1 className="text-xl font-bold tracking-tight text-[#0b1426]">Scout <span className="text-cyan-600">/</span> Control Centre</h1></div>
        </div>
        <span className="rounded-full border border-cyan-200 bg-cyan-50 px-3 py-1.5 text-[10px] font-bold tracking-wider text-[#16456b]">PRIVATE ADMIN</span>
      </header>

      <nav className="flex items-center gap-1 border-b border-slate-200 py-2" aria-label="Main navigation">
        <button className={`rounded-md px-3 py-2 text-sm font-semibold transition-colors ${page === "jobs" ? "bg-[#0b1426] text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"}`} onClick={() => setPage("jobs")}>Jobs</button>
        <button className={`rounded-md px-3 py-2 text-sm font-semibold transition-colors ${page === "companies" ? "bg-[#0b1426] text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"}`} onClick={() => setPage("companies")}>Companies</button>
        <button className="ml-auto rounded-md bg-cyan-500 px-3 py-2 text-sm font-semibold text-[#071426] shadow-sm hover:bg-cyan-400" onClick={() => { setPage("add-company"); setError(""); setNotice(""); }}>+ Add company</button>
      </nav>

      {error && <div className="alert error" role="alert">{error}</div>}
      {notice && <div className="alert success" role="status">{notice}</div>}

      {page === "jobs" && (
        <section className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
          <div className="flex items-center justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.2em] text-cyan-700">Operations overview</p><h2 className="text-xl font-bold tracking-tight text-[#0b1426]">Ingestion dashboard <span className="ml-2 text-xs font-medium text-slate-500">{loading ? "Refreshing…" : "Live workspace data"}</span></h2></div><Button onClick={() => void extractJobs()} disabled={extracting || loading} className="bg-[#0b1426] text-white shadow-md hover:bg-[#142c4c]"><RefreshCw className={`h-4 w-4 ${extracting ? "animate-spin" : ""}`} />{extracting ? "Extracting…" : "Run extraction"}</Button></div>
          <div className="grid grid-cols-2 gap-2 xl:grid-cols-4">
            {[
              { label:"Collected vacancies", value:vacancies.length, note:"Active records", icon:BriefcaseBusiness, color:"text-cyan-700", bg:"bg-cyan-50" },
              { label:"Registered companies", value:employers.length, note:"Employer records", icon:Building2, color:"text-blue-700", bg:"bg-blue-50" },
              { label:"New in last 24 hours", value:newVacancies24h, note:"Based on first seen time", icon:Sparkles, color:"text-emerald-700", bg:"bg-emerald-50" },
              { label:"Needs admin attention", value:attentionCount, note:"Pending or needs verification", icon:CircleAlert, color:"text-amber-700", bg:"bg-amber-50" },
            ].map(({label,value,note,icon:Icon,color,bg}) => <div key={label} className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm"><span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${bg} ${color}`}><Icon className="h-5 w-5" /></span><div className="min-w-0"><p className="text-[11px] font-medium text-slate-500">{label}</p><p className="text-xl font-bold leading-tight text-[#0b1426]">{value}</p><p className="text-[10px] text-slate-400">{note}</p></div></div>)}
          </div>
          <section className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <div className="mb-2 flex items-center justify-between"><h3 className="flex items-center gap-2 text-xs font-bold text-[#0b1426]"><Activity className="h-4 w-4 text-cyan-600" /> ATS performance</h3><span className="text-[10px] text-slate-400">Source health and latest extraction results</span></div>
            <div className="grid gap-2 md:grid-cols-2">
              {atsPerformance.map((item) => <div key={item.adapter} className="flex items-center justify-between gap-3 rounded-lg bg-slate-50 px-3 py-2">
                <div className="min-w-0"><p className="text-xs font-bold capitalize text-slate-800">{item.adapter}</p><p className="text-[10px] text-slate-500">{item.sourceCount} sources · {item.verified} verified · {item.jobCount} vacancies</p></div>
                <div className="text-right"><Badge variant={item.latest && ["success","empty"].includes(item.latest.outcome) ? "default" : item.latest && item.latest.outcome !== "running" ? "destructive" : "secondary"} className="capitalize">{item.latest?.outcome ?? "No runs"}</Badge><p className="mt-1 text-[10px] text-slate-500">{item.latest ? `${item.latest.jobs_inserted} new · ${item.failed} failed runs` : "Awaiting first extraction"}</p></div>
              </div>)}
            </div>
          </section>
          <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
            <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 bg-slate-50/80 p-3"><h3 className="mr-auto text-sm font-bold text-[#0b1426]">{showArchived ? "Archived vacancies" : "Vacancy records"}</h3>
                <Select value={showArchived ? "archived" : "active"} onValueChange={(value) => { setShowArchived(value === "archived"); setSelectedVacancy(null); setSelectedVacancyId(null); }}><SelectTrigger className="h-8 w-[125px] bg-white text-xs"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="active">Active records</SelectItem><SelectItem value="archived">Archived</SelectItem></SelectContent></Select>
                <Select value={reviewFilter} onValueChange={setReviewFilter}><SelectTrigger className="h-8 w-[145px] bg-white text-xs"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">All review states</SelectItem><SelectItem value="pending">Pending</SelectItem><SelectItem value="needs_verification">Needs verification</SelectItem><SelectItem value="verified">Verified</SelectItem><SelectItem value="rejected">Rejected</SelectItem></SelectContent></Select>
                <Select value={selectedEmployerId} onValueChange={setSelectedEmployerId}><SelectTrigger className="h-8 w-[140px] bg-white text-xs"><SelectValue placeholder="All companies" /></SelectTrigger><SelectContent><SelectItem value="all">All companies</SelectItem>{employers.map((employer) => <SelectItem key={employer.id} value={employer.id}>{employer.name}</SelectItem>)}</SelectContent></Select>
                <Button variant="outline" size="sm" className="h-8 bg-white" onClick={() => void loadWorkspace()} disabled={loading}>Refresh</Button>
              </div>
              <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
                {loading ? <p className="py-12 text-center text-sm text-slate-500">Loading operational data…</p> : filteredVacancies.length === 0 ? <div className="py-12 text-center"><p className="text-sm font-semibold">No matching records</p><p className="mt-1 text-xs text-slate-500">Adjust the filters or register a source.</p></div> : filteredVacancies.map((vacancy) => <button key={vacancy.id} type="button" onClick={() => void openVacancy(vacancy.id)} aria-pressed={selectedVacancyId === vacancy.id} className={`w-full rounded-lg border p-3 text-left shadow-sm transition-all hover:border-cyan-300 hover:bg-cyan-50/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 ${selectedVacancyId === vacancy.id ? "border-cyan-500 bg-cyan-50 shadow-[inset_4px_0_0_#06b6d4,0_2px_8px_#0b14261a]" : "border-slate-200 bg-white"}`}>
                  <span className="flex items-start justify-between gap-3"><strong className="text-sm font-semibold leading-snug text-[#0b1426]">{vacancy.title}</strong><Badge variant={vacancy.review_status === "verified" ? "default" : vacancy.review_status === "rejected" ? "destructive" : "secondary"} className={vacancy.review_status === "pending" ? "bg-amber-100 text-amber-800 hover:bg-amber-100" : vacancy.review_status === "needs_verification" ? "bg-orange-100 text-orange-800 hover:bg-orange-100" : ""}>{vacancy.review_status.replaceAll("_", " ")}</Badge></span>
                  <span className="mt-1 block text-xs font-medium text-slate-600">{vacancy.employer_name}</span><span className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[10px] text-slate-500"><span>{vacancy.location_text || "Location unknown"}</span>{vacancy.department && <span>{vacancy.department}</span>}<span>First seen {new Date(vacancy.first_seen_at ?? vacancy.last_seen_at).toLocaleDateString()}</span></span>
                </button>)}
              </div>
            </section>
            <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              {openingVacancyId ? <div className="grid flex-1 place-content-center text-center text-sm text-slate-500">Loading vacancy…</div> : selectedVacancy ? <>
                <div className="flex items-center justify-between gap-3 border-b border-slate-100 bg-[#0b1426] p-4 text-white"><div className="min-w-0"><p className="text-[10px] font-medium text-cyan-300">{selectedVacancy.employer_name} · {selectedVacancy.location_text || "Location unknown"}</p><h3 className="mt-1 text-sm font-bold">{selectedVacancy.title}</h3></div><Button variant="ghost" size="sm" className="text-slate-300 hover:bg-white/10 hover:text-white" onClick={() => { setSelectedVacancy(null); setSelectedVacancyId(null); }}>Clear</Button></div>
                <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 px-4 py-3"><Button asChild size="sm" className="bg-cyan-500 text-[#071426] hover:bg-cyan-400"><a href={selectedVacancy.application_url} target="_blank" rel="noreferrer">Open source listing ↗</a></Button><Button asChild size="sm" variant="outline"><a href={selectedVacancy.source_url} target="_blank" rel="noreferrer">Source record ↗</a></Button><Badge className="bg-amber-100 text-amber-800">{selectedVacancy.review_status.replaceAll("_", " ")}</Badge></div>
                <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
                  <div><h4 className="mb-2 text-sm font-bold text-[#0b1426]">Extracted description</h4>{selectedVacancy.description ? <iframe className="h-[min(42vh,500px)] min-h-[280px] w-full rounded-lg border border-slate-200 bg-white" title={"Description for " + selectedVacancy.title} sandbox="" srcDoc={"<!doctype html><html><head><meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src https: data:; style-src 'unsafe-inline';\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>body{font:14px/1.65 system-ui,sans-serif;color:#263449;margin:18px;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:#168bb9}img{max-width:100%;height:auto}ul,ol{padding-left:24px}</style></head><body>" + decodeGreenhouseContent(selectedVacancy.description) + "</body></html>"} /> : <p className="rounded-lg bg-amber-50 p-4 text-sm text-amber-800">No description was saved by the source. Inspect the source listing.</p>}</div>
                  <section className="rounded-lg border border-slate-200"><div className="border-b bg-slate-50 px-3 py-2"><h4 className="text-xs font-bold text-[#0b1426]">Admin review actions</h4><p className="mt-1 text-[10px] text-slate-500">Pending is the database default; it does not mean automated verification has run.</p></div><div className="space-y-3 p-3"><label className="grid gap-1 text-xs font-medium text-slate-600">Decision notes<input className="h-9 rounded-md border border-slate-200 bg-white px-3 text-sm font-normal" value={reviewReason} disabled={Boolean(selectedVacancy.archived_at)} onChange={(event) => setReviewReason(event.target.value)} placeholder="Record the reason for your decision" /></label><div className="flex flex-wrap gap-2"><Button size="sm" disabled={vacancySaving || Boolean(selectedVacancy.archived_at)} onClick={() => void setVacancyDecision("verified") } className="bg-emerald-600 text-white hover:bg-emerald-700"><ShieldCheck className="h-4 w-4" />Mark verified</Button><Button size="sm" variant="outline" disabled={vacancySaving || Boolean(selectedVacancy.archived_at)} onClick={() => void setVacancyDecision("needs_verification")}>Needs verification</Button><Button size="sm" variant="destructive" disabled={vacancySaving || Boolean(selectedVacancy.archived_at)} onClick={() => void setVacancyDecision("rejected")}>Reject record</Button>{selectedVacancy.archived_at ? <Button size="sm" onClick={() => void restoreSelectedVacancy()}>Restore</Button> : <Button size="sm" variant="outline" onClick={() => void archiveSelectedVacancy()}>Archive</Button>}</div></div></section>
                  <details className="rounded-lg border border-slate-200"><summary className="cursor-pointer px-3 py-2 text-xs font-semibold text-slate-700">Publishing payload preview</summary><pre className="max-h-64 overflow-auto border-t bg-slate-50 p-3 text-xs">{JSON.stringify({title:selectedVacancy.title,company:selectedVacancy.employer_name,location:selectedVacancy.location_text,review_status:selectedVacancy.review_status,review_reason:selectedVacancy.review_reason,application_url:selectedVacancy.application_url,source_url:selectedVacancy.source_url},null,2)}</pre></details>
                </div>
              </> : <div className="grid flex-1 place-content-center px-6 text-center"><p className="text-sm font-semibold text-[#0b1426]">Select a vacancy record</p><p className="mt-1 max-w-xs text-xs text-slate-500">Inspect extracted content and resolve records requiring admin attention.</p></div>}
            </section>
          </div>
        </section>
      )}

      {page === "companies" && (
        <>
          <section className="page-heading">
            <div><p className="eyebrow">EMPLOYER DIRECTORY</p><h2>Companies</h2><p>Manage registered employers and their official job sources.</p></div>
            <button className="button primary" onClick={() => setPage("add-company")}>+ Add company</button>
          </section>
          <div className="company-layout">
            <section className="surface company-directory">
              <div className="section-heading"><h3>Registered companies</h3><span>{employers.length}</span></div>
              {employers.map((employer) => (
                <button key={employer.id} className={`company-row ${selectedEmployerId === employer.id ? "selected" : ""}`} onClick={() => void openCompany(employer)}>
                  {employer.logo_url
                    ? <img className="employer-logo" src={employer.logo_url} alt={employer.name + " logo"} />
                    : <span className="employer-avatar">{employer.name.slice(0, 1).toUpperCase()}</span>}
                  <span><strong>{employer.name}</strong><small>{employer.city || "Location not confirmed"}</small></span>
                  <span className="status">{employer.status.replaceAll("_", " ")}</span>
                </button>
              ))}
              {!employers.length && <div className="empty">No companies registered.</div>}
            </section>
            <section className="surface company-profile">
              {selectedEmployer ? (
                <>
                  <div className="section-heading"><div><p className="eyebrow">COMPANY PROFILE</p><h3>{selectedEmployer.name}</h3></div><span className="status">{selectedEmployer.status.replaceAll("_", " ")}</span></div>
                  <p className="profile-website">{selectedEmployer.website_url || "Official website not supplied"}</p>
                  <form className="branding-form" onSubmit={saveEmployerBranding}>
                    <h4>Company logo</h4>
                    <label>Logo image URL
                      <input type="url" value={logoUrl} onChange={(event) => setLogoUrl(event.target.value)} placeholder="https://company.com/logo.png" />
                    </label>
                    <label>Logo source / evidence URL
                      <input type="url" value={logoSourceUrl} onChange={(event) => setLogoSourceUrl(event.target.value)} placeholder="Official company page where the logo is shown" />
                    </label>
                    <button className="button secondary" disabled={saving}>{saving ? "Saving…" : "Save logo details"}</button>
                  </form>

                  <div className="profile-stats"><div><strong>{vacancies.filter((item) => item.employer_id === selectedEmployer.id).length}</strong><span>Jobs collected</span></div><div><strong>{sources.length}</strong><span>Sources registered</span></div></div>
                  <div className="section-heading source-title"><h4>Job sources</h4></div>
                  {sources.length ? sources.map((source) => {
                    const runs = extractionRuns[source.id] ?? [];
                    const latestRun = runs[0];
                    return (
                      <div className="source-history" key={source.id}>
                        <div className="source-item">
                          <div><strong>{source.adapter_key}</strong><small>{source.source_url}</small></div>
                          <span className="status">{source.status.replaceAll("_", " ")}</span>
                          {source.adapter_key === "greenhouse" && <button className="button secondary" type="button" onClick={() => { setEditingSourceId(source.id); setSourceUrl(source.source_url); setInspection(null); }}>Edit source</button>}
                        </div>
                        <div className="run-history">
                          <div className="run-heading"><strong>Latest extraction</strong><span>{runs.length} recorded run(s)</span></div>
                          {latestRun ? (
                            <>
                              <div className="run-summary">
                                <span className={`run-outcome ${latestRun.outcome}`}>{latestRun.outcome.replaceAll("_", " ")}</span>
                                <span>{latestRun.jobs_received} received · {latestRun.jobs_inserted} new · {latestRun.jobs_updated} updated</span>
                                <span>{latestRun.complete ? "Complete" : "Incomplete"}</span>
                              </div>
                              {latestRun.detail && <p className="run-detail">{latestRun.detail}</p>}
                              <div className="run-meta">
                                <span>Started: {latestRun.started_at ? new Date(latestRun.started_at).toLocaleString() : "Unknown"}</span>
                                <span>Finished: {latestRun.finished_at ? new Date(latestRun.finished_at).toLocaleString() : "Not finished"}</span>
                              </div>
                              {runs.length > 1 && <details className="run-older"><summary>Previous runs ({runs.length - 1})</summary>{runs.slice(1).map((run) => <div className="older-run" key={run.id}><strong>{run.outcome.replaceAll("_", " ")}</strong><span>{run.jobs_received} received · {run.jobs_inserted} new · {run.jobs_updated} updated</span><small>{run.detail || "No additional detail"}</small><small>{run.started_at ? new Date(run.started_at).toLocaleString() : "Unknown time"}</small></div>)}</details>}
                            </>
                          ) : <p className="muted">No extraction runs recorded yet.</p>}
                        </div>
                      </div>
                    );
                  }) : <p className="muted">No job source registered for this company.</p>}
                  <form className="source-form" onSubmit={createSource}>
                    <h4>{editingSourceId ? "Update Greenhouse source" : "Register Greenhouse source"}</h4>
                    <label>Official careers / job board URL<input type="url" value={sourceUrl} onChange={(event) => { setSourceUrl(event.target.value); setInspection(null); }} placeholder="https://job-boards.greenhouse.io/company" required /></label>
                    <button type="button" className="button secondary" onClick={() => void inspectGreenhouse()} disabled={inspecting || !sourceUrl.trim()}>{inspecting ? "Checking source…" : "Check Greenhouse source"}</button>
                    {inspection && <div className="inspection-preview"><strong>{inspection.board_name || inspection.board_token}</strong><span>{inspection.outcome} · {inspection.jobs.length} sample jobs</span>{inspection.detail && <small>{inspection.detail}</small>}</div>}
                    <div className="form-actions">{editingSourceId && <button type="button" className="button secondary" onClick={() => { setEditingSourceId(null); setSourceUrl(""); setInspection(null); }}>Cancel edit</button>}<button className="button primary" disabled={saving || !inspection || !inspection.complete || !["success", "empty"].includes(inspection.outcome)}>{saving ? "Saving…" : editingSourceId ? "Update source" : "Save source"}</button></div>
                  </form>
                </>
              ) : <div className="empty large"><strong>Select a company</strong><span>Choose a company to view its profile and registered job sources.</span></div>}
            </section>
          </div>
        </>
      )}

      {page === "add-company" && (
        <>
          <section className="page-heading">
            <div><p className="eyebrow">EMPLOYER ONBOARDING</p><h2>Add a company</h2><p>Paste the official careers or jobs listing URL. Scout will identify its ATS.</p></div>
          </section>
          <section className="surface add-company-panel">
            <form onSubmit={discovery ? registerDiscoveredEmployer : (event) => { event.preventDefault(); void discoverCareersPage(); }}>
              <label>Careers / jobs listing URL
                <input type="url" value={sourceUrl} onChange={(event) => { setSourceUrl(event.target.value); setDiscovery(null); setForm({ ...form, website_url: event.target.value }); }} placeholder="https://company.com/jobs" required />
              </label>
              <label>ATS platform
                <select value={atsKey} onChange={(event) => { setAtsKey(event.target.value); setDiscovery(null); }}>
                  <option value="greenhouse">Greenhouse</option>
                  <option value="workday" disabled>Workday — coming next</option>
                </select>
              </label>
              <button type="button" className="button secondary" onClick={() => void discoverCareersPage()} disabled={inspecting || !sourceUrl.trim()}>
                {inspecting ? "Detecting ATS and inspecting jobs…" : "Detect ATS & preview jobs"}
              </button>
              {discovery && (
                <div className="inspection-preview">
                  <strong>{discovery.jobs.length} vacancies found</strong>
                  <span>Detected: {discovery.detected_adapter} · Board: {discovery.board_url}</span>
                  <small>{discovery.complete ? "Vacancy preview is complete." : discovery.detail || "The preview is incomplete."}</small>
                </div>
              )}
              {discovery && <label>Company name
                <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Detected company name" required />
              </label>}
              <div className="form-actions">
                <button type="button" className="button secondary" onClick={() => { setPage("companies"); setDiscovery(null); }}>Cancel</button>
                {discovery && <button className="button primary" disabled={saving || !discovery.complete || !["success", "empty"].includes(discovery.outcome)}>
                  {saving ? "Registering and retrieving…" : "Confirm & register"}
                </button>}
              </div>
            </form>
          </section>
        </>
      )}

      <footer className="mt-5 border-t pt-3 text-xs text-muted-foreground">Scout is a private operations workspace. Only verified, quality-checked records are eligible for publishing to Thungatha.</footer>
    </main>
  );
}
