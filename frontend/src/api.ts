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

export export type Vacancy = {
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
  last_seen_at: string;
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
  return response.json() as Promise<T>;
}

export const scoutApi = {
  listEmployers: () => request<Employer[]>("/api/v1/employers"),
  createEmployer: (payload: Record<string, unknown>) =>
    request<Employer>("/api/v1/employers", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listSources: (employerId: string) =>
    request<EmployerSource[]>(`/api/v1/employers/${employerId}/sources`),
  createSource: (employerId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources`, {
      method: "POST",
      body: JSON.stringify({ ...payload, employer_id: employerId }),
    }),
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
  inspectGreenhouse: (url: string) =>
    request<GreenhouseInspection>(
      `/api/v1/greenhouse/inspect?url=${encodeURIComponent(url)}`,
    ),
};
