import { request } from "./scout-http-client";
import type {
  CareersDiscovery,
  GreenhouseInspection,
} from "../shared-contracts/discovery-contracts";

export const discoveryApiClient = {
  discoverCareersPage: (url: string) =>
    request<CareersDiscovery>(
      `/api/v1/greenhouse/discover?url=${encodeURIComponent(url)}`,
    ),

  inspectGreenhouse: (url: string) =>
    request<GreenhouseInspection>(
      `/api/v1/greenhouse/inspect?url=${encodeURIComponent(url)}`,
    ),
};
