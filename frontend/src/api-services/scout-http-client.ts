import { supabase } from "./supabase-auth-client";

export const API_BASE = (import.meta.env.VITE_SCOUT_API_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);

export type ProblemDetails = {
  title?: string;
  detail?: string;
  status?: number;
};

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const { data } = (await supabase?.auth.getSession()) ?? { data: { session: null } };
  const accessToken = data.session?.access_token;
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(`Cannot reach Scout API at ${API_BASE}. Start the backend and try again.`);
  }

  if (!response.ok) {
    const problem = (await response.json().catch(() => ({}))) as ProblemDetails;
    throw new Error(problem.detail ?? problem.title ?? `Request failed (${response.status}).`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
