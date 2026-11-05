import { request } from "./scout-http-client";
import type { ExtractionRun } from "../shared-contracts/vacancy-contracts";

export const extractionApiClient = {
  extractSource: (sourceId: string) =>
    request<ExtractionRun>(`/api/v1/sources/${sourceId}/extract`, {
      method: "POST",
    }),

  listExtractionRuns: (sourceId: string) =>
    request<ExtractionRun[]>(`/api/v1/sources/${sourceId}/extraction-runs`),

  listAllExtractionRuns: () => request<ExtractionRun[]>("/api/v1/extraction-runs"),
};
