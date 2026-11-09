import { request } from "./scout-http-client";
import type { ExtractionRun } from "../shared-contracts/vacancy-contracts";

export const extractionApiClient = {
  previewSource: (sourceId: string) =>
    request<{
      outcome: string;
      complete: boolean;
      detail: string | null;
      discovery_preview: {
        total_vacancies: number;
        jobs: { id: string | number; title: string }[];
      };
    }>("/api/v1/sources/" + sourceId + "/preview", { method: "POST" }),

  extractSource: (sourceId: string) =>
    request<ExtractionRun>(`/api/v1/sources/${sourceId}/extract`, {
      method: "POST",
    }),

  listExtractionRuns: (sourceId: string) =>
    request<ExtractionRun[]>(`/api/v1/sources/${sourceId}/extraction-runs`),

  listAllExtractionRuns: () => request<ExtractionRun[]>("/api/v1/extraction-runs"),
};
