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
};
