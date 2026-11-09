import { request } from "./scout-http-client";
import type { CareersDiscovery, SourceInspection } from "../shared-contracts/discovery-contracts";

function isLeverBoardUrl(value: string): boolean {
  try {
    return ["jobs.lever.co", "jobs.eu.lever.co"].includes(new URL(value).hostname);
  } catch {
    return false;
  }
}

export const discoveryApiClient = {
  discoverCareersPage: async (url: string, companyName: string) => {
    const path = isLeverBoardUrl(url) ? "/api/v1/lever/discover" : "/api/v1/greenhouse/discover";
    const result = await request<CareersDiscovery>(
      `${path}?url=${encodeURIComponent(url)}&company_name=${encodeURIComponent(companyName)}`,
    );
    return {
      ...result,
      adapter_config: result.adapter_config ?? { slug: result.board_token },
    };
  },

  inspectSource: async (url: string): Promise<SourceInspection> => {
    if (isLeverBoardUrl(url)) {
      return request<SourceInspection>(`/api/v1/lever/inspect?url=${encodeURIComponent(url)}`);
    }
    const result = await request<Omit<SourceInspection, "detected_adapter" | "adapter_config">>(
      `/api/v1/greenhouse/inspect?url=${encodeURIComponent(url)}`,
    );
    return {
      ...result,
      detected_adapter: "greenhouse",
      adapter_config: { slug: result.board_token },
    };
  },
};
