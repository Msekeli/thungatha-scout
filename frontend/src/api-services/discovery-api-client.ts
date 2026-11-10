import { request } from "./scout-http-client";
import type { CareersDiscovery, SourceInspection } from "../shared-contracts/discovery-contracts";

function isLeverBoardUrl(value: string): boolean {
  try {
    return ["jobs.lever.co", "jobs.eu.lever.co"].includes(new URL(value).hostname);
  } catch {
    return false;
  }
}

function displayNameFromSlug(slug: string): string {
  return slug
    .replace(/[-_.]+/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase())
    .trim();
}

async function discoverTeamtailor(url: string, companyName: string) {
  return request<CareersDiscovery>(
    `/api/v1/teamtailor/discover?url=${encodeURIComponent(url)}&company_name=${encodeURIComponent(companyName)}`,
  );
}

async function discoverGreenhouse(url: string, companyName: string) {
  return request<CareersDiscovery>(
    `/api/v1/greenhouse/discover?url=${encodeURIComponent(url)}&company_name=${encodeURIComponent(companyName)}`,
  );
}

export const discoveryApiClient = {
  discoverCareersPage: async (url: string, companyName: string) => {
    if (isLeverBoardUrl(url)) {
      const result = await request<CareersDiscovery>(
        `/api/v1/lever/discover?url=${encodeURIComponent(url)}&company_name=${encodeURIComponent(companyName)}`,
      );
      const slug = result.board_token || new URL(url).pathname.split("/").filter(Boolean)[0] || "";
      const detectedName =
        result.board_name?.trim() ||
        result.company_name?.trim() ||
        displayNameFromSlug(slug);
      return {
        ...result,
        board_name: result.board_name || detectedName,
        company_name: result.company_name || detectedName,
        adapter_config: result.adapter_config ?? { slug },
      };
    }
    try {
      return await discoverTeamtailor(url, companyName);
    } catch {
      return discoverGreenhouse(url, companyName);
    }
  },

  inspectSource: async (url: string): Promise<SourceInspection> => {
    if (isLeverBoardUrl(url)) {
      return request<SourceInspection>(
        `/api/v1/lever/inspect?url=${encodeURIComponent(url)}`,
      );
    }
    try {
      return await request<SourceInspection>(
        `/api/v1/teamtailor/inspect?url=${encodeURIComponent(url)}`,
      );
    } catch {
      const result = await request<
        Omit<SourceInspection, "detected_adapter" | "adapter_config">
      >(`/api/v1/greenhouse/inspect?url=${encodeURIComponent(url)}`);
      return {
        ...result,
        detected_adapter: "greenhouse",
        adapter_config: { slug: result.board_token },
      };
    }
  },
};
