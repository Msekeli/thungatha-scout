import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, GreenhouseInspection, Vacancy } from "./api";

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
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [selectedEmployerId, setSelectedEmployerId] = useState("all");
  const [sources, setSources] = useState<EmployerSource[]>([]);
  const [form, setForm] = useState(emptyEmployer);
  const [sourceUrl, setSourceUrl] = useState("");
  const [inspection, setInspection] = useState<GreenhouseInspection | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [inspecting, setInspecting] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const selectedEmployer = employers.find((item) => item.id === selectedEmployerId) ?? null;
  const filteredVacancies = useMemo(
    () => selectedEmployerId === "all"
      ? vacancies
      : vacancies.filter((item) => item.employer_id === selectedEmployerId),
    [vacancies, selectedEmployerId],
  );

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextEmployers, nextVacancies] = await Promise.all([
        scoutApi.listEmployers(),
        scoutApi.listVacancies(),
      ]);
      setEmployers(nextEmployers);
      setVacancies(nextVacancies);
      if (selectedEmployerId !== "all" && !nextEmployers.some((item) => item.id === selectedEmployerId)) {
        setSelectedEmployerId("all");
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load Scout data.");
    } finally {
      setLoading(false);
    }
  }, [selectedEmployerId]);

  useEffect(() => { void loadWorkspace(); }, [loadWorkspace]);

  async function openCompany(employer: Employer) {
    setSelectedEmployerId(employer.id);
    setPage("companies");
    setError("");
    try {
      setSources(await scoutApi.listSources(employer.id));
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
      const results = [];
      for (const item of greenhouseSources) {
        results.push({ employer: item.employer, run: await scoutApi.extractSource(item.source.id) });
      }
      const [nextVacancies] = await Promise.all([scoutApi.listVacancies()]);
      setVacancies(nextVacancies);
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

  async function createEmployer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const created = await scoutApi.createEmployer({
        ...form,
        website_url: form.website_url || null,
      });
      setForm(emptyEmployer);
      await loadWorkspace();
      setSelectedEmployerId(created.id);
      setSources([]);
      setPage("companies");
      setNotice(`${created.name} added. Register its official Greenhouse source from the company profile.`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not add company.");
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
      const created = await scoutApi.createSource(selectedEmployer.id, {
        adapter_key: "greenhouse",
        source_url: sourceUrl,
        normalized_url: sourceUrl,
        employer_careers_url: selectedEmployer.website_url ?? null,
        adapter_config: { slug: inspection?.board_token },
      });
      setSources((current) => [...current, created]);
      setSourceUrl("");
      setInspection(null);
      setNotice("Greenhouse source registered. Verification and permission remain pending.");
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
              <div><h3>All vacancies</h3><p className="muted">Select a company to narrow the list.</p></div>
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
                  <thead><tr><th>Position</th><th>Company</th><th>Location</th><th>Last seen</th><th></th></tr></thead>
                  <tbody>
                    {filteredVacancies.map((vacancy) => (
                      <tr key={vacancy.id}>
                        <td><strong>{vacancy.title}</strong>{vacancy.department && <small>{vacancy.department}</small>}</td>
                        <td><button className="text-link" onClick={() => { const employer = employers.find((item) => item.id === vacancy.employer_id); if (employer) void openCompany(employer); }}>{vacancy.employer_name}</button></td>
                        <td>{vacancy.location_text || "Not specified"}</td>
                        <td>{new Date(vacancy.last_seen_at).toLocaleDateString()}</td>
                        <td><a href={vacancy.application_url} target="_blank" rel="noreferrer">View job ↗</a></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
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
                  <span className="employer-avatar">{employer.name.slice(0, 1).toUpperCase()}</span>
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
                  <div className="profile-stats"><div><strong>{vacancies.filter((item) => item.employer_id === selectedEmployer.id).length}</strong><span>Jobs collected</span></div><div><strong>{sources.length}</strong><span>Sources registered</span></div></div>
                  <div className="section-heading source-title"><h4>Job sources</h4></div>
                  {sources.length ? sources.map((source) => <div className="source-item" key={source.id}><div><strong>{source.adapter_key}</strong><small>{source.source_url}</small></div><span className="status">{source.status.replaceAll("_", " ")}</span></div>) : <p className="muted">No job source registered for this company.</p>}
                  <form className="source-form" onSubmit={createSource}>
                    <h4>Register Greenhouse source</h4>
                    <label>Official careers / job board URL<input type="url" value={sourceUrl} onChange={(event) => { setSourceUrl(event.target.value); setInspection(null); }} placeholder="https://job-boards.greenhouse.io/company" required /></label>
                    <button type="button" className="button secondary" onClick={() => void inspectGreenhouse()} disabled={inspecting || !sourceUrl.trim()}>{inspecting ? "Checking source…" : "Check Greenhouse source"}</button>
                    {inspection && <div className="inspection-preview"><strong>{inspection.board_name || inspection.board_token}</strong><span>{inspection.outcome} · {inspection.jobs.length} sample jobs</span>{inspection.detail && <small>{inspection.detail}</small>}</div>}
                    <button className="button primary" disabled={saving || !inspection || !inspection.complete || !["success", "empty"].includes(inspection.outcome)}>{saving ? "Saving…" : "Save source"}</button>
                  </form>
                </>
              ) : <div className="empty large"><strong>Select a company</strong><span>Choose a company to view its profile and registered job sources.</span></div>}
            </section>
          </div>
        </>
      )}

      {page === "add-company" && (
        <>
          <section className="page-heading"><div><p className="eyebrow">EMPLOYER ONBOARDING</p><h2>Add a company</h2><p>Register the employer first. You can add and verify its job source from its profile.</p></div></section>
          <section className="surface add-company-panel">
            <form onSubmit={createEmployer}>
              <label>Company name<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Company name" required /></label>
              <label>Official website<input type="url" value={form.website_url} onChange={(event) => setForm({ ...form, website_url: event.target.value })} placeholder="https://company.co.za" /></label>
              <label>Organization type<select value={form.organization_type} onChange={(event) => setForm({ ...form, organization_type: event.target.value })}><option value="unresolved">Needs classification</option><option value="direct_employer">Direct employer</option><option value="recruitment_agency">Recruitment agency</option><option value="staffing_company">Staffing company</option><option value="hybrid">Hybrid</option><option value="other">Other</option></select></label>
              <div className="form-row"><label>City<input value={form.city} onChange={(event) => setForm({ ...form, city: event.target.value })} /></label><label>Province<input value={form.province} onChange={(event) => setForm({ ...form, province: event.target.value })} /></label></div>
              <label>Country<input value={form.country} onChange={(event) => setForm({ ...form, country: event.target.value })} /></label>
              <div className="form-actions"><button type="button" className="button secondary" onClick={() => setPage("companies")}>Cancel</button><button className="button primary" disabled={saving}>{saving ? "Saving company…" : "Add company"}</button></div>
            </form>
          </section>
        </>
      )}

      <footer>Scout is a private operations workspace. Only verified, quality-checked records are eligible for publishing to Thungatha.</footer>
    </main>
  );
}
