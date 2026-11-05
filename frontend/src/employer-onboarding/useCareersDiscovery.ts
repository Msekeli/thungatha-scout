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

  async function discover(
    sourceUrl: string,
    companyName: string,
    onCompanyNameDetected: (name: string) => void,
  ) {
    setInspecting(true);
    onError("");
    onNotice("");
    setDiscovery(null);
    try {
      if (atsKey !== "greenhouse") {
        throw new Error("Workday discovery will be enabled in the Workday vertical slice.");
      }
      const result = await scoutApi.discoverCareersPage(sourceUrl, companyName);
      setDiscovery(result);
      onCompanyNameDetected(result.board_name || result.company_name || "");
      onNotice("Greenhouse board confirmed. Register the company to start extraction.");
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
