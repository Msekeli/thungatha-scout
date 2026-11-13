import { request } from "./scout-http-client";
import {
  isGreenhouseBoardUrl,
  isLeverBoardUrl,
  isTeamtailorBoardUrl,
  isWorkableBoardUrl,
  isWorkdayBoardUrl,
} from "./careers-board-url-detection";
import type {
  CareersDiscovery,
  SourceInspection,
} from "../shared-contracts/discovery-contracts";

function discoverKnownBoard(url: string, companyName: string) {
  const query =
    `url=${encodeURIComponent(url)}&company_name=${encodeURIComponent(companyName)}`;
  if (isWorkdayBoardUrl(url)) {
    return request<CareersDiscovery>(`/api/v1/workday/discover?${query}`);
  }
  if (isWorkableBoardUrl(url))
    return request<CareersDiscovery>(`/api/v1/workable/discover?${query}`);
  if (isLeverBoardUrl(url)) {
    return request<CareersDiscovery>(`/api/v1/lever/discover?${query}`);
  }
  if (isGreenhouseBoardUrl(url))
    return request<CareersDiscovery>(`/api/v1/greenhouse/discover?${query}`);
  if (isTeamtailorBoardUrl(url))
    return request<CareersDiscovery>(`/api/v1/teamtailor/discover?${query}`);
  return null;
}

async function discoverGenericPage(url: string, companyName: string) {
  return request<CareersDiscovery>(
    `/api/v1/career-pages/discover?url=${encodeURIComponent(url)}` +
      `&company_name=${encodeURIComponent(companyName)}`,
  );
}

export const discoveryApiClient = {
  discoverCareersPage: async (url: string, companyName: string) => {
    const known = await discoverKnownBoard(url, companyName);
    return known ?? discoverGenericPage(url, companyName);
  },

  inspectSource: async (url: string): Promise<SourceInspection> => {
    const known = discoverKnownBoard(url, "");
    if (known) {
      const result = await known;
      return {
        ...result,
        source_url: url,
        outcome: result.outcome ?? "success",
        jobs: result.jobs ?? [],
        pages_fetched: result.pages_fetched ?? 0,
        complete: result.complete ?? false,
        detail: result.detail ?? null,
      };
    }
    return request<SourceInspection>(
      `/api/v1/career-pages/discover?url=${encodeURIComponent(url)}`,
    );
  },
};
