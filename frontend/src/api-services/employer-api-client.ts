import { request } from "./scout-http-client";
import type { Employer } from "../shared-contracts/employer-contracts";

export type EmployerUpdate = {
  name: string;
  legal_name?: string | null;
  website_url?: string | null;
  organization_type: string;
  city?: string | null;
  province?: string | null;
  country?: string | null;
};

export const employerApiClient = {
  listEmployers: () => request<Employer[]>("/api/v1/employers"),
  createEmployer: (payload: Record<string, unknown>) =>
    request<Employer>("/api/v1/employers", { method: "POST", body: JSON.stringify(payload) }),
  updateEmployer: (employerId: string, payload: EmployerUpdate) =>
    request<Employer>(`/api/v1/employers/${employerId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  deleteEmployer: (employerId: string) =>
    request<void>(`/api/v1/employers/${employerId}`, { method: "DELETE" }),
  updateEmployerBranding: (employerId: string, logo_url: string, logo_source_url: string, logo_type: string) =>
    request<Employer>(`/api/v1/employers/${employerId}/branding`, {
      method: "PATCH",
      body: JSON.stringify({
        logo_url: logo_url || null,
        logo_source_url: logo_source_url || null,
        logo_type,
      }),
    }),
  discoverEmployerLogo: (employerId: string) =>
    request<Employer | null>(`/api/v1/employers/${employerId}/branding/discover`, {
      method: "POST",
    }),
};
