import { useState } from "react";
import { scoutApi } from "../api";
import type { CareersDiscovery, GreenhouseInspection } from "../api";

type UseCareersDiscoveryOptions = {
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export function useCareersDiscovery({ onError, onNotice }: UseCareersDiscoveryOptions) {
  const [discovery, setDiscovery] = useState<CareersDiscovery | null>(null);
  const [inspection, setInspection] = useState<GreenhouseInspection | null>(null);
  const [atsKey, setAtsKey] = useState("greenhouse");
  const [inspecting, setInspecting] = useState(false);

  async function discover(sourceUrl: string, onCompanyNameDetected: (name: string) => void) {
    setInspecting(true);
    onError("");
    onNotice("");
    setDiscovery(null);
    try {
      if (atsKey !== "greenhouse") {
        throw new Error("Workday discovery will be enabled in the Workday vertical slice.");
      }
      const result = await scoutApi.discoverCareersPage(sourceUrl);
      setDiscovery(result);
      onCompanyNameDetected(result.company_name ?? "");
      onNotice(`Detected ${result.detected_adapter} and found ${result.jobs.length} vacancies.`);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not discover the careers source.");
    } finally {
      setInspecting(false);
    }
  }

  async function inspectGreenhouseBoard(sourceUrl: string) {
    setInspecting(true);
    onError("");
    setInspection(null);
    try {
      setInspection(await scoutApi.inspectGreenhouse(sourceUrl));
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not inspect Greenhouse board.");
    } finally {
      setInspecting(false);
    }
  }

  return {
    discovery,
    setDiscovery,
    inspection,
    setInspection,
    atsKey,
    setAtsKey,
    inspecting,
    discover,
    inspectGreenhouseBoard,
  };
}
