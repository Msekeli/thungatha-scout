import { request } from "./scout-http-client";
import type { EmployerSource } from "../shared-contracts/employer-contracts";

export const employerSourceApiClient = {
  listSources: (employerId: string) =>
    request<EmployerSource[]>(`/api/v1/employers/${employerId}/sources`),
  listAllSources: () => request<EmployerSource[]>("/api/v1/employers/sources"),
  createSource: (employerId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources`, {
      method: "POST", body: JSON.stringify({ ...payload, employer_id: employerId }),
    }),
  updateSource: (employerId: string, sourceId: string, payload: Record<string, unknown>) =>
    request<EmployerSource>(`/api/v1/employers/${employerId}/sources/${sourceId}`, {
      method: "PUT", body: JSON.stringify(payload),
    }),
};
