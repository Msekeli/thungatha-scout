import { request } from "./scout-http-client";
import type {
  Vacancy,
  VacancyLocationScope,
  VacancyPage,
} from "../shared-contracts/vacancy-contracts";

type VacancyPageQuery = {
  employerId?: string;
  locationScope: VacancyLocationScope;
  limit?: number;
  offset?: number;
};

export type VacancyDashboardMetrics = { total_active: number; new_last_24_hours: number };

export const vacancyApiClient = {
  getVacancyMetrics: () => request<VacancyDashboardMetrics>("/api/v1/vacancies/metrics"),
  listVacancies: (query: VacancyPageQuery = { locationScope: "south_africa" }) => {
    const params = new URLSearchParams({
      location_scope: query.locationScope,
      limit: String(query.limit ?? 50),
      offset: String(query.offset ?? 0),
    });
    if (query.employerId && query.employerId !== "all") params.set("employer_id", query.employerId);
    return request<VacancyPage>(`/api/v1/vacancies?${params.toString()}`);
  },
  getVacancy: (vacancyId: string) => request<Vacancy>(`/api/v1/vacancies/${vacancyId}`),
  archiveVacancy: (vacancyId: string, reason: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/archive`, {
      method: "POST",
      body: JSON.stringify({ reason: reason || null }),
    }),
  restoreVacancy: (vacancyId: string) =>
    request<Vacancy>(`/api/v1/vacancies/${vacancyId}/restore`, { method: "POST" }),
  listArchivedVacancies: () => request<Vacancy[]>(`/api/v1/vacancies/archived`),
};
