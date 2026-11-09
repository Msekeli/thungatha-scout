import { useState } from "react";
import { scoutApi } from "../api";
import type { CareersDiscovery, SourceInspection } from "../api";

type UseCareersDiscoveryOptions = {
  onError: (message: string) => void;
};

export function useCareersDiscovery({ onError }: UseCareersDiscoveryOptions) {
  const [inspection, setInspection] = useState<SourceInspection | null>(null);
  const [inspecting, setInspecting] = useState(false);

  async function discover(
    sourceUrl: string,
    companyName: string,
    onCompanyNameDetected: (name: string) => void,
  ): Promise<CareersDiscovery | null> {
    setInspecting(true);
    onError("");
    try {
      const result = await scoutApi.discoverCareersPage(sourceUrl, companyName);
      onCompanyNameDetected(result.board_name || result.company_name || "");
      return result;
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not inspect this careers page.");
      return null;
    } finally {
      setInspecting(false);
    }
  }

  async function inspectSource(sourceUrl: string) {
    setInspecting(true);
    onError("");
    setInspection(null);
    try {
      setInspection(await scoutApi.inspectSource(sourceUrl));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not inspect this recruitment source.");
    } finally {
      setInspecting(false);
    }
  }

  return { inspection, setInspection, inspecting, discover, inspectSource };
}
