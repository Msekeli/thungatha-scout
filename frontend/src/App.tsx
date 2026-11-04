import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, GreenhouseInspection } from "./api";

const emptyEmployer = {
  name: "",
  website_url: "",
  organization_type: "unresolved",
  city: "Cape Town",
  province: "Western Cape",
  country: "South Africa",
};

export default function App() {
  const [employers, setEmployers] = useState<Employer[]>([]);
  const [selected, setSelected] = useState<Employer | null>(null);
  const [sources, setSources] = useState<EmployerSource[]>([]);
  const [form, setForm] = useState(emptyEmployer);
  const [sourceUrl, setSourceUrl] = useState("");
  const [greenhouseInspection, setGreenhouseInspection] = useState<GreenhouseInspection | null>(null);
  const [inspecting, setInspecting] = useState(false);
  const [adapter, setAdapter] = useState<"greenhouse" | "workday">("greenhouse");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadEmployers = useCallback(async (selectedEmployerId?: string) => {
    setLoading(true);
    setError("");
    try {
      const result = await scoutApi.listEmployers();
      setEmployers(result);
      if (selectedEmployerId) {
        const refreshed =
          result.find((item) => item.id === selectedEmployerId) ?? null;
        setSelected(refreshed);
        setSources(
          refreshed ? await scoutApi.listSources(refreshed.id) : [],
        );
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load employers.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadEmployers();
  }, [loadEmployers]);

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
      setSelected(created);
      setSources([]);
      setNotice(`${created.name} added to the registry.`);
      const result = await scoutApi.listEmployers();
      setEmployers(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not create employer.");
    } finally {
      setSaving(false);
    }
  }

  async function selectEmployer(employer: Employer) {
    setSelected(employer);
    setError("");
    try {
      setSources(await scoutApi.listSources(employer.id));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not load sources.");
    }
  }

  async function inspectGreenhouse() {
    setInspecting(true);
    setError("");
    setNotice("");
    setGreenhouseInspection(null);
    try {
      const result = await scoutApi.inspectGreenhouse(sourceUrl);
      setGreenhouseInspection(result);
      if (result.outcome === "success" || result.outcome === "empty") {
        setNotice(`Greenhouse board found: ${result.board_name ?? result.board_token}.`);
      } else {
        setError(result.detail ?? `Greenhouse inspection: ${result.outcome}.`);
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not inspect Greenhouse board.");
    } finally {
      setInspecting(false);
    }
  }

  async function createSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const created = await scoutApi.createSource(selected.id, {
        adapter_key: adapter,
        source_url: sourceUrl,
        normalized_url: sourceUrl,
        employer_careers_url: selected.website_url ?? null,
        adapter_config: adapter === "greenhouse"
          ? { slug: greenhouseInspection?.board_token }
          : {},
      });
      setSources((current) => [...current, created]);
      setSourceUrl("");
      setGreenhouseInspection(null);
      setNotice("Source added. Verification and permission remain pending.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Could not add source.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">THUNGATHA / OPERATIONS</p>
          <h1>Scout</h1>
        </div>
        <span className="environment">LOCAL ADMIN</span>
      </header>

      <section className="intro">
        <div>
          <p className="eyebrow">EMPLOYER INTELLIGENCE</p>
          <h2>Employer registry</h2>
          <p>Register employers and their official vacancy sources before extraction.</p>
        </div>
        <div className="stat">
          <strong>{employers.length}</strong>
          <span>Employers registered</span>
        </div>
      </section>

      {error && <div className="alert error" role="alert">{error}</div>}
      {notice && <div className="alert success" role="status">{notice}</div>}

      <div className="workspace">
        <section className="surface registry">
          <div className="section-heading">
            <div><p className="eyebrow">REGISTRY</p><h3>Employers</h3></div>
            <button className="button secondary" onClick={() => void loadEmployers(selected?.id)}>Refresh</button>
          </div>
          {loading ? <p className="muted">Loading registry…</p> : employers.length === 0 ? (
            <div className="empty"><strong>No employers yet</strong><span>Add your first employer using the form.</span></div>
          ) : (
            <div className="employer-list">
              {employers.map((employer) => (
                <button
                  className={`employer-item ${selected?.id === employer.id ? "selected" : ""}`}
                  key={employer.id}
                  onClick={() => void selectEmployer(employer)}
                >
                  <span className="employer-avatar">{employer.name.slice(0, 1).toUpperCase()}</span>
                  <span className="employer-copy"><strong>{employer.name}</strong><small>{employer.city ?? "Location unresolved"}</small></span>
                  <span className="status">{employer.status.replaceAll("_", " ")}</span>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="surface details">
          {selected ? (
            <>
              <div className="section-heading">
                <div><p className="eyebrow">EMPLOYER PROFILE</p><h3>{selected.name}</h3></div>
                <span className="status">{selected.organization_type.replaceAll("_", " ")}</span>
              </div>
              <p className="muted">{selected.website_url || "Official website not supplied"}</p>
              <div className="source-heading"><h4>Vacancy sources</h4><span>{sources.length} registered</span></div>
              {sources.length === 0 ? <p className="muted">No ATS source registered yet.</p> : (
                <div className="source-list">
                  {sources.map((source) => (
                    <div className="source-item" key={source.id}>
                      <div><strong>{source.adapter_key}</strong><small>{source.source_url}</small></div>
                      <span className="status">{source.status.replaceAll("_", " ")}</span>
                    </div>
                  ))}
                </div>
              )}
              <form className="source-form" onSubmit={createSource}>
                <h4>Add a source</h4>
                <label>ATS platform
                  <select value={adapter} onChange={(event) => setAdapter(event.target.value as "greenhouse" | "workday")}>
                    <option value="greenhouse">Greenhouse</option>
                    <option value="workday" disabled>Workday — planned for M4</option>
                  </select>
                </label>
                <label>Careers / board URL
                  <input type="url" value={sourceUrl} onChange={(event) => { setSourceUrl(event.target.value); setGreenhouseInspection(null); }} placeholder="https://…" required />
                </label>
                {adapter === "greenhouse" && (
                  <button className="button secondary" type="button" onClick={() => void inspectGreenhouse()} disabled={inspecting || !sourceUrl.trim()}>
                    {inspecting ? "Inspecting board…" : "Inspect Greenhouse board"}
                  </button>
                )}
                {greenhouseInspection && (
                  <div className="inspection-preview">
                    <strong>{greenhouseInspection.board_name ?? greenhouseInspection.board_token}</strong>
                    <span>{greenhouseInspection.outcome} · {greenhouseInspection.jobs.length} jobs · {greenhouseInspection.pages_fetched} page(s)</span>
                    {greenhouseInspection.jobs.slice(0, 5).map((job) => (
                      <a key={job.id} href={job.absolute_url} target="_blank" rel="noreferrer">{job.title}</a>
                    ))}
                    {!greenhouseInspection.complete && <small>Inventory is incomplete. Do not use this result for lifecycle reconciliation.</small>}
                  </div>
                )}
                <button className="button primary" disabled={saving || (adapter === "greenhouse" && (!greenhouseInspection || !greenhouseInspection.complete || !["success", "empty"].includes(greenhouseInspection.outcome)))}>{saving ? "Saving…" : "Add source"}</button>
              </form>
            </>
          ) : (
            <div className="empty large"><strong>Select an employer</strong><span>Choose an employer to inspect its sources or add an ATS board.</span></div>
          )}
        </section>

        <section className="surface create">
          <div className="section-heading"><div><p className="eyebrow">NEW RECORD</p><h3>Add employer</h3></div></div>
          <form onSubmit={createEmployer}>
            <label>Employer name<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Company name" required /></label>
            <label>Official website<input type="url" value={form.website_url} onChange={(event) => setForm({ ...form, website_url: event.target.value })} placeholder="https://company.co.za" /></label>
            <label>Organization type
              <select value={form.organization_type} onChange={(event) => setForm({ ...form, organization_type: event.target.value })}>
                <option value="unresolved">Unresolved</option>
                <option value="direct_employer">Direct employer</option>
                <option value="recruitment_agency">Recruitment agency</option>
                <option value="staffing_company">Staffing company</option>
                <option value="hybrid">Hybrid</option>
                <option value="other">Other</option>
              </select>
            </label>
            <div className="form-row">
              <label>City<input value={form.city} onChange={(event) => setForm({ ...form, city: event.target.value })} /></label>
              <label>Province<input value={form.province} onChange={(event) => setForm({ ...form, province: event.target.value })} /></label>
            </div>
            <label>Country<input value={form.country} onChange={(event) => setForm({ ...form, country: event.target.value })} /></label>
            <button className="button primary" disabled={saving}>{saving ? "Saving…" : "Create employer"}</button>
          </form>
        </section>
      </div>
      <footer>Scout stores source claims as discovered. Adding a URL does not verify employer identity, source ownership or permission.</footer>
    </main>
  );
}
