import { request } from "./scout-http-client";
import type { EmployerSource } from "../shared-contracts/employer-contracts";

export type SourceReviewPayload = {
  status: string;
  permission_status: string;
  evidence_url: string;
  reason: string;
};

export const employerSourceApiClient = {
  listSources: (employerId: string) =>
    request<EmployerSource[]>(`/api/v1/employers/${employerId}/sources`),

  listAllSources: () => request<EmployerSource[]>("/api/v1/employers/sources"),

  createSource: (employerId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources`, {
      method: "POST",
      body: JSON.stringify({ ...payload, employer_id: employerId }),
    }),

  updateSource: (employerId: string, sourceId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources/${sourceId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  updateSourceReview: (employerId: string, sourceId: string, payload: SourceReviewPayload) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources/${sourceId}/review`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
};
