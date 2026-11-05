import { request } from "./scout-http-client";
import type {
  Vacancy,
  VacancyLocationScope,
  VacancyPage,
  VacancyReviewStatus,
} from "../shared-contracts/vacancy-contracts";

type VacancyPageQuery = {
  employerId?: string;
  reviewStatus?: VacancyReviewStatus | "all";
  locationScope: VacancyLocationScope;
  limit?: number;
  offset?: number;
};

export const vacancyApiClient = {
  listVacancies: (query: VacancyPageQuery = { locationScope: "cape_town" }) => {
    const params = new URLSearchParams({
      location_scope: query.locationScope,
      limit: String(query.limit ?? 50),
      offset: String(query.offset ?? 0),
    });
    if (query.employerId && query.employerId !== "all") params.set("employer_id", query.employerId);
    if (query.reviewStatus && query.reviewStatus !== "all") {
      params.set("review_status", query.reviewStatus);
    }
    return request<VacancyPage>(`/api/v1/vacancies?${params.toString()}`);
  },
  getVacancy: (vacancyId: string) => request<Vacancy>(`/api/v1/vacancies/${vacancyId}`),
  updateVacancyReview: (
    vacancyId: string,
    review_status: Vacancy["review_status"],
    review_reason: string,
  ) =>
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
  listArchivedVacancies: () => request<Vacancy[]>(`/api/v1/vacancies/archived`),
};
