import { request } from "./scout-http-client";
import type { Vacancy } from "../shared-contracts/vacancy-contracts";

export const vacancyApiClient = {
  listVacancies: (employerId?: string) =>
    request<Vacancy[]>(employerId ? `/api/v1/employers/${employerId}/vacancies` : "/api/v1/vacancies"),
  getVacancy: (vacancyId: string) => request<Vacancy>(`/api/v1/vacancies/${vacancyId}`),
  updateVacancyReview: (vacancyId: string, review_status: Vacancy["review_status"], review_reason: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/review`, {
      method: "PATCH", body: JSON.stringify({ review_status, review_reason: review_reason || null }),
    }),
  archiveVacancy: (vacancyId: string, reason: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/archive`, {
      method: "POST", body: JSON.stringify({ reason: reason || null }),
    }),
  restoreVacancy: (vacancyId: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/restore`, { method: "POST" }),
  listArchivedVacancies: () => request<Vacancy[]>("/api/v1/vacancies/archived"),
};
