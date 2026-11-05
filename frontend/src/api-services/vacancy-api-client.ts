import { request } from "./scout-http-client";
import type { Vacancy } from "../shared-contracts/vacancy-contracts";

export type VacancyLocationScope = "cape_town" | "all";

export const vacancyApiClient = {
  listVacancies: (locationScope: VacancyLocationScope = "cape_town") =>
    request<Vacancy[]>(`/api/v1/vacancies?location_scope=${locationScope}`),

  getVacancy: (vacancyId: string) => request<Vacancy>(`/api/v1/vacancies/${vacancyId}`),

  updateVacancyReview: (
    vacancyId: string,
    review_status: Vacancy["review_status"],
    review_reason: string,
  ) => request<Vacancy>(`/api/v1/vacancies/${vacancyId}/review`, {
    method: "PATCH",
    body: JSON.stringify({ review_status, review_reason: review_reason || null }),
  }),

  archiveVacancy: (vacancyId: string, reason: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/archive`, {
      method: "POST", body: JSON.stringify({ reason: reason || null }),
    }),
  restoreVacancy: (vacancyId: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/restore`, { method: "POST" }),
  listArchivedVacancies: () => request<Vacancy[]>("/api/v1/vacancies/archived"),
};