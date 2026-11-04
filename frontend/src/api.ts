const API_BASE = (
  import.meta.env.VITE_SCOUT_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export type Employer = {
  id: string;
  name: string;
  legal_name?: string | null;
  website_url?: string | null;
  organization_type: string;
  status: string;
  city?: string | null;
  province?: string | null;
  country?: string | null;
  logo_url?: string | null;
  logo_source_url?: string | null;
  created_at?: string;
};

export type EmployerSource = {
  id: string;
  employer_id: string;
  adapter_key: "greenhouse" | "workday";
  source_url: string;
  normalized_url: string;
  status: string;
  permission_status: string;
};

export type Vacancy = {
  id: string;
  employer_id: string;
  employer_name: string;
  source_id: string;
  external_job_id: string;
  title: string;
  description?: string | null;
  location_text?: string | null;
  department?: string | null;
  office?: string | null;
  source_url: string;
  application_url: string;
  source_updated_at?: string | null;
  first_seen_at?: string;
  last_seen_at: string;
  review_status: "pending" | "needs_verification" | "verified" | "rejected";
  review_reason?: string | null;
  reviewed_at?: string | null;
  archived_at?: string | null;
  archived_reason?: string | null;
  employer_logo_url?: string | null;
  employer_logo_source_url?: string | null;
};

export type ExtractionRun = {
  id: string;
  source_id: string;
  outcome: string;
  jobs_received: number;
  jobs_inserted: number;
  jobs_updated: number;
  complete: boolean;
  detail?: string | null;
  started_at?: string;
  finished_at?: string | null;
};

export type CareersDiscovery = GreenhouseInspection & {
  careers_url: string;
  board_url: string;
  detected_adapter: "greenhouse";
  company_name?: string;
};

export type GreenhouseInspection = {
  outcome: string;
  board_token: string;
  board_name: string | null;
  jobs: Array<{
    id: number;
    title: string;
    absolute_url: string;
    location?: { name?: string };
    content?: string;
  }>;
  pages_fetched: number;
  complete: boolean;
  detail: string | null;
  source_url: string;
};

type ProblemDetails = { title?: string; detail?: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(
      `Cannot reach Scout API at ${API_BASE}. Start the backend and try again.`,
    );
  }

  if (!response.ok) {
    const problem = (await response.json().catch(() => ({}))) as ProblemDetails;
    throw new Error(
      problem.detail ?? problem.title ?? `Request failed (${response.status}).`,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const scoutApi = {
  listEmployers: () => request<Employer[]>("/api/v1/employers"),
  createEmployer: (payload: Record<string, unknown>) =>
    request<Employer>("/api/v1/employers", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updateEmployerStatus: (employerId: string, status: "approved" | "needs_review" | "rejected" | "inactive") =>
    request<Employer>(`/api/v1/employers/${employerId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  deleteEmployer: (employerId: string) =>
    request<void>(`/api/v1/employers/${employerId}`, { method: "DELETE" }),
  updateEmployerBranding: (employerId: string, logo_url: string, logo_source_url: string) =>
    request<Employer>(`/api/v1/employers/${employerId}/branding`, {
      method: "PATCH",
      body: JSON.stringify({ logo_url: logo_url || null, logo_source_url: logo_source_url || null }),
    }),
  listSources: (employerId: string) =>
    request<EmployerSource[]>(`/api/v1/employers/${employerId}/sources`),
  updateSource: (employerId: string, sourceId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources/${sourceId}`, {
      method: "PUT", body: JSON.stringify(payload),
    }),
  updateSourceReview: (employerId: string, sourceId: string, payload: { status: string; permission_status: string; evidence_url: string; reason: string }) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources/${sourceId}/review`, {
      method: "PATCH", body: JSON.stringify(payload),
    }),
  createSource: (employerId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources`, {
      method: "POST",
      body: JSON.stringify({ ...payload, employer_id: employerId }),
    }),
  getVacancy: (vacancyId: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}`),
  updateVacancyReview: (vacancyId: string, review_status: Vacancy["review_status"], review_reason: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/review`, {
      method: "PATCH",
      body: JSON.stringify({ review_status, review_reason: review_reason || null }),
    }),
  archiveVacancy: (vacancyId: string, reason: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/archive`, {
      method: "POST",
      body: JSON.stringify({ reason: reason || null }),
    }),
  restoreVacancy: (vacancyId: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/restore`, { method: "POST" }),
  listArchivedVacancies: () => request<Vacancy[]>("/api/v1/vacancies/archived"),
  listVacancies: (employerId?: string) =>
    request<Vacancy[]>(
      employerId
        ? `/api/v1/employers/${employerId}/vacancies`
        : "/api/v1/vacancies",
    ),
  extractSource: (sourceId: string) =>
    request<ExtractionRun>(`/api/v1/sources/${sourceId}/extract`, {
      method: "POST",
    }),
  listExtractionRuns: (sourceId: string) =>
    request<ExtractionRun[]>(`/api/v1/sources/${sourceId}/extraction-runs`),
  discoverCareersPage: (url: string) =>
    request<CareersDiscovery>(
      `/api/v1/greenhouse/discover?url=${encodeURIComponent(url)}`,
    ),
  inspectGreenhouse: (url: string) =>
    request<GreenhouseInspection>(
      `/api/v1/greenhouse/inspect?url=${encodeURIComponent(url)}`,
    ),
};
