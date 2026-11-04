import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, ExtractionRun, GreenhouseInspection, CareersDiscovery, Vacancy } from "./api";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

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
  const [reviewReason, setReviewReason] = useState("");
  const [logoUrl, setLogoUrl] = useState("");
  const [logoSourceUrl, setLogoSourceUrl] = useState("");
  const [vacancySaving, setVacancySaving] = useState(false);
  const [selectedEmployerId, setSelectedEmployerId] = useState("all");
  const [sources, setSources] = useState<EmployerSource[]>([]);
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
    setError("");
    setSelectedVacancyId(vacancyId);
    setOpeningVacancyId(vacancyId);
    setSelectedVacancy(null);
    try {
      const vacancy = await scoutApi.getVacancy(vacancyId);
      setSelectedVacancy(vacancy);
      setReviewReason(vacancy.review_reason ?? "");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load vacancy details.");
      setSelectedVacancyId(null);
    } finally {
      setOpeningVacancyId(null);
    }
  }

  async function saveVacancyReview() {
    if (!selectedVacancy) return;
    setVacancySaving(true);
    setError("");
    try {
      const updated = await scoutApi.updateVacancyReview(
        selectedVacancy.id,
        selectedVacancy.review_status,
        reviewReason,
      );
      setSelectedVacancy(updated);
      setVacancies((current) => current.map((item) => item.id === updated.id ? updated : item));
      setNotice("Vacancy review status saved.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not update vacancy review.");
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
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark">S</span>
          <div><p className="eyebrow">THUNGATHA / OPERATIONS</p><h1>Scout</h1></div>
        </div>
        <span className="environment">PRIVATE ADMIN</span>
      </header>

      <nav className="main-nav" aria-label="Main navigation">
        <button className={page === "jobs" ? "active" : ""} onClick={() => setPage("jobs")}>Jobs</button>
        <button className={page === "companies" ? "active" : ""} onClick={() => setPage("companies")}>Companies</button>
        <button className="nav-add" onClick={() => { setPage("add-company"); setError(""); setNotice(""); }}>+ Add company</button>
      </nav>

      {error && <div className="alert error" role="alert">{error}</div>}
      {notice && <div className="alert success" role="status">{notice}</div>}

      {page === "jobs" && (
        <>
          <section className="page-heading">
            <div><p className="eyebrow">VACANCY WORKSPACE</p><h2>Jobs</h2><p>Collected vacancies from your registered companies.</p></div>
            <button className="button primary extract-button" onClick={() => void extractJobs()} disabled={extracting || loading}>
              {extracting ? "Extracting jobs…" : "↻ Extract jobs"}
            </button>
          </section>
          <section className="metric-row">
            <div className="metric-card"><span>Companies</span><strong>{employers.length}</strong></div>
            <div className="metric-card"><span>Collected jobs</span><strong>{vacancies.length}</strong></div>
            <div className="metric-card"><span>Companies with jobs</span><strong>{new Set(vacancies.map((item) => item.employer_id)).size}</strong></div>
          </section>
          <section className="surface jobs-panel">
            <div className="jobs-toolbar">
              <div><h3>{showArchived ? "Archived vacancies" : "All vacancies"}</h3><p className="muted">Select a company to narrow the list.</p></div>
              <select aria-label="Filter active or archived jobs" value={showArchived ? "archived" : "active"} onChange={(event) => { setShowArchived(event.target.value === "archived"); setSelectedVacancy(null); }}>
                <option value="active">Active jobs</option>
                <option value="archived">Archived jobs</option>
              </select>
              <select aria-label="Filter jobs by review status" value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value)}>
                <option value="all">All review states</option>
                <option value="pending">Pending</option>
                <option value="needs_verification">Needs verification</option>
                <option value="verified">Verified</option>
                <option value="rejected">Rejected</option>
              </select>
              <select aria-label="Filter jobs by company" value={selectedEmployerId} onChange={(event) => setSelectedEmployerId(event.target.value)}>
                <option value="all">All companies</option>
                {employers.map((employer) => <option key={employer.id} value={employer.id}>{employer.name}</option>)}
              </select>
              <button className="button secondary" onClick={() => void loadWorkspace()} disabled={loading}>Refresh</button>
            </div>
            {loading ? <div className="empty">Loading jobs…</div> : filteredVacancies.length === 0 ? (
              <div className="empty"><strong>No jobs collected yet</strong><span>Register a company source, then select “Extract jobs”.</span></div>
            ) : (
              <div className="jobs-table-wrap">
                <table className="jobs-table">
                  <thead><tr><th>Position</th><th>Company</th><th>Location</th><th>Review</th><th>Last seen</th><th></th></tr></thead>
                  <tbody>
                    {filteredVacancies.map((vacancy) => (
                      <tr key={vacancy.id}>
                        <td><button className="text-link vacancy-title" onClick={() => void openVacancy(vacancy.id)}>{vacancy.title}</button>{vacancy.department && <small>{vacancy.department}</small>}</td>
                        <td><button className="text-link" onClick={() => { const employer = employers.find((item) => item.id === vacancy.employer_id); if (employer) void openCompany(employer); }}>{vacancy.employer_name}</button></td>
                        <td>{vacancy.location_text || "Not specified"}</td>
                        <td><span className={`review-state ${vacancy.review_status}`}>{vacancy.review_status.replaceAll("_", " ")}</span></td>
                        <td>{new Date(vacancy.last_seen_at).toLocaleDateString()}</td>
                        <td className="vacancy-actions">
                          <button className="text-link" onClick={() => void openVacancy(vacancy.id)}>View details</button>
                          <a href={vacancy.application_url} target="_blank" rel="noreferrer">Open original ↗</a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          <div className="jobs-workspace">
            <section className="surface jobs-panel">
              <div className="jobs-toolbar">
                <div><h3>{showArchived ? "Archived vacancies" : "All vacancies"}</h3><p className="muted">Select a company to view its details.</p></div>
                <select aria-label="Filter active or archived jobs" value={showArchived ? "archived" : "active"} onChange={(event) => { setShowArchived(event.target.value === "archived"); setSelectedVacancy(null); setSelectedVacancyId(null); }}>
                  <option value="active">Active jobs</option>
                  <option value="archived">Archived jobs</option>
                </select>
                <select aria-label="Filter jobs by review status" value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value)}>
                  <option value="all">All review states</option>
                  <option value="pending">Pending</option>
                  <option value="needs_verification">Needs verification</option>
                  <option value="verified">Verified</option>
                  <option value="rejected">Rejected</option>
                </select>
                <select aria-label="Filter jobs by company" value={selectedEmployerId} onChange={(event) => setSelectedEmployerId(event.target.value)}>
                  <option value="all">All companies</option>
                  {employers.map((employer) => <option key={employer.id} value={employer.id}>{employer.name}</option>)}
                </select>
                <Button variant="outline" size="sm" onClick={() => void loadWorkspace()} disabled={loading}>Refresh</Button>
              </div>
              {loading ? <div className="empty">Loading jobs…</div> : filteredVacancies.length === 0 ? (
                <div className="empty"><strong>No jobs collected yet</strong><span>Register a company source, then select “Extract jobs”.</span></div>
              ) : (
                <div className="jobs-table-wrap">
                  <table className="jobs-table">
                    <thead><tr><th>Position</th><th>Company</th><th>Location</th><th>Review</th><th>Last seen</th></tr></thead>
                    <tbody>
                      {filteredVacancies.map((vacancy) => (
                        <tr key={vacancy.id} className={selectedVacancyId === vacancy.id ? "selected" : ""}>
                          <td>
                            <button className="text-link vacancy-title" onClick={() => void openVacancy(vacancy.id)}>{vacancy.title}</button>
                            {vacancy.department && <small>{vacancy.department}</small>}
                          </td>
                          <td><button className="text-link" onClick={() => { const employer = employers.find((item) => item.id === vacancy.employer_id); if (employer) void openCompany(employer); }}>{vacancy.employer_name}</button></td>
                          <td>{vacancy.location_text || "Not specified"}</td>
                          <td><Badge variant={vacancy.review_status === "verified" ? "default" : vacancy.review_status === "rejected" ? "destructive" : "secondary"}>{vacancy.review_status.replaceAll("_", " ")}</Badge></td>
                          <td>{new Date(vacancy.last_seen_at).toLocaleDateString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="surface vacancy-detail">
              {openingVacancyId ? (
                <div className="empty large"><strong>Loading vacancy details…</strong><span>Retrieving the full job record.</span></div>
              ) : selectedVacancy ? (
                <>
                  <div className="section-heading">
                    <div className="vacancy-identity">
                      {selectedVacancy.employer_logo_url
                        ? <img className="employer-logo" src={selectedVacancy.employer_logo_url} alt={selectedVacancy.employer_name + " logo"} />
                        : <span className="employer-avatar">{selectedVacancy.employer_name.slice(0, 1).toUpperCase()}</span>}
                      <div><p className="eyebrow">VACANCY DETAILS</p><h3>{selectedVacancy.title}</h3><p className="muted">{selectedVacancy.employer_name} · {selectedVacancy.location_text || "Location not specified"}</p></div>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => { setSelectedVacancy(null); setSelectedVacancyId(null); }}>Clear selection</Button>
                  </div>
                  <div className="detail-links">
                    <a href={selectedVacancy.source_url} target="_blank" rel="noreferrer">Greenhouse board ↗</a>
                    <a href={selectedVacancy.application_url} target="_blank" rel="noreferrer">Open original job / apply ↗</a>
                  </div>
                  <div className="vacancy-review">
                    <div><label>Review status
                      <select value={selectedVacancy.review_status} disabled={Boolean(selectedVacancy.archived_at)} onChange={(event) => setSelectedVacancy({ ...selectedVacancy, review_status: event.target.value as Vacancy["review_status"] })}>
                        <option value="pending">Pending</option>
                        <option value="needs_verification">Needs verification</option>
                        <option value="verified">Verified</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </label></div>
                    <div><label>Review reason / notes
                      <input value={reviewReason} disabled={Boolean(selectedVacancy.archived_at)} onChange={(event) => setReviewReason(event.target.value)} placeholder="Explain what needs checking…" />
                    </label></div>
                    <div className="review-actions">
                      {!selectedVacancy.archived_at
                        ? <><Button size="sm" onClick={() => void saveVacancyReview()} disabled={vacancySaving}>Save review</Button><Button variant="outline" size="sm" onClick={() => void archiveSelectedVacancy()} disabled={vacancySaving}>Archive vacancy</Button></>
                        : <Button size="sm" onClick={() => void restoreSelectedVacancy()} disabled={vacancySaving}>Restore vacancy</Button>}
                    </div>
                  </div>
                  <div className="detail-grid">
                    <div>
                      <h4>Full job description</h4>
                      {selectedVacancy.description ? (
                        <iframe className="description-frame" title={"Description for " + selectedVacancy.title} sandbox="" srcDoc={"<!doctype html><html><head><meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; img-src https: data:; style-src 'unsafe-inline';\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>body{font:14px/1.65 system-ui,sans-serif;color:#263449;margin:18px;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:#315b9a}img{max-width:100%;height:auto}ul,ol{padding-left:24px}</style></head><body>" + decodeGreenhouseContent(selectedVacancy.description || "") + "</body></html>"} />
                      ) : <p className="empty">Greenhouse did not return description content for this vacancy.</p>}
                    </div>
                    <div>
                      <h4>Thungatha payload preview</h4>
                      <p className="muted">Draft mapping for inspection only. Nothing is published from this screen.</p>
                      <pre className="payload-preview">{JSON.stringify({
                        title: selectedVacancy.title,
                        company: selectedVacancy.employer_name,
                        location: selectedVacancy.location_text,
                        description: selectedVacancy.description ? decodeGreenhouseContent(selectedVacancy.description) : null,
                        review_status: selectedVacancy.review_status,
                        review_reason: selectedVacancy.review_reason,
                        application_url: selectedVacancy.application_url,
                        source_url: selectedVacancy.source_url,
                        department: selectedVacancy.department,
                        office: selectedVacancy.office,
                      }, null, 2)}</pre>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty large vacancy-placeholder">
                  <strong>Select a vacancy</strong>
                  <span>Choose a job from the list to inspect its description, review status and publishing payload.</span>
                </div>
              )}
            </section>
          </div>
        </>
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

      <footer>Scout is a private operations workspace. Only verified, quality-checked records are eligible for publishing to Thungatha.</footer>
    </main>
  );
}
