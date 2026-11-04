import { useState, useCallback } from "react";
import type { EmployerSource } from "../shared-contracts/employer-contracts";
import type { ExtractionRun } from "../shared-contracts/vacancy-contracts";
import type { GreenhouseInspection } from "../shared-contracts/discovery-contracts";
import { employerSourceApiClient } from "../api-services/employer-source-api-client";
import { extractionApiClient } from "../api-services/extraction-api-client";
import { discoveryApiClient } from "../api-services/discovery-api-client";

export function useEmployerSourceManagement(
  onNotice: (msg: string) => void,
  onError: (msg: string) => void,
) {
  const [sources, setSources] = useState<EmployerSource[]>([]);
  const [extractionRuns, setExtractionRuns] = useState<Record<string, ExtractionRun[]>>({});
  const [sourceUrl, setSourceUrl] = useState("");
  const [editingSourceId, setEditingSourceId] = useState<string | null>(null);
  const [inspection, setInspection] = useState<GreenhouseInspection | null>(null);
  const [inspecting, setInspecting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [reviewSourceId, setReviewSourceId] = useState<string | null>(null);
  const [reviewStatus, setReviewStatus] = useState("verified");
  const [permissionStatus, setPermissionStatus] = useState("allowed");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [decisionReason, setDecisionReason] = useState("");

  const loadSources = useCallback(
    async (employerId: string) => {
      try {
        const nextSources = await employerSourceApiClient.listSources(employerId);
        setSources(nextSources);
        const runEntries = await Promise.all(
          nextSources.map(
            async (s) => [s.id, await extractionApiClient.listExtractionRuns(s.id)] as const,
          ),
        );
        setExtractionRuns((prev) => ({ ...prev, ...Object.fromEntries(runEntries) }));
      } catch (err) {
        onError(err instanceof Error ? err.message : "Could not load company sources.");
      }
    },
    [onError],
  );

  const inspectSource = useCallback(async () => {
    setInspecting(true);
    setInspection(null);
    try {
      setInspection(await discoveryApiClient.inspectGreenhouse(sourceUrl));
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not inspect Greenhouse board.");
    } finally {
      setInspecting(false);
    }
  }, [sourceUrl, onError]);

  const saveSource = useCallback(
    async (employerId: string, employerWebsite?: string | null) => {
      setSaving(true);
      try {
        const payload = {
          adapter_key: "greenhouse",
          source_url: sourceUrl,
          normalized_url: sourceUrl,
          adapter_config: { slug: inspection?.board_token },
        };
        if (editingSourceId) {
          await employerSourceApiClient.updateSource(employerId, editingSourceId, payload);
          onNotice("Source updated. Verification state preserved.");
        } else {
          const created = await employerSourceApiClient.createSource(employerId, {
            ...payload,
            employer_careers_url: employerWebsite ?? null,
          });
          setSources((prev) => [...prev, created]);
          onNotice("Greenhouse source registered. Verification pending.");
        }
        setEditingSourceId(null);
        setSourceUrl("");
        setInspection(null);
      } catch (err) {
        onError(err instanceof Error ? err.message : "Could not save source.");
      } finally {
        setSaving(false);
      }
    },
    [sourceUrl, inspection, editingSourceId, onNotice, onError],
  );

  const saveReview = useCallback(
    async (employerId: string) => {
      if (!reviewSourceId) return;
      setSaving(true);
      try {
        const updated = await employerSourceApiClient.updateSourceReview(
          employerId,
          reviewSourceId,
          {
            status: reviewStatus,
            permission_status: permissionStatus,
            evidence_url: evidenceUrl,
            reason: decisionReason,
          },
        );
        setSources((prev) => prev.map((s) => (s.id === updated.id ? updated : s)));
        setReviewModalOpen(false);
        onNotice("Source verification decision recorded.");
      } catch (err) {
        onError(err instanceof Error ? err.message : "Could not update source review.");
      } finally {
        setSaving(false);
      }
    },
    [
      reviewSourceId,
      reviewStatus,
      permissionStatus,
      evidenceUrl,
      decisionReason,
      onNotice,
      onError,
    ],
  );

  return {
    sources,
    setSources,
    extractionRuns,
    setExtractionRuns,
    sourceUrl,
    setSourceUrl,
    editingSourceId,
    setEditingSourceId,
    inspection,
    setInspection,
    inspecting,
    saving,
    reviewModalOpen,
    setReviewModalOpen,
    reviewStatus,
    setReviewStatus,
    permissionStatus,
    setPermissionStatus,
    evidenceUrl,
    setEvidenceUrl,
    decisionReason,
    setDecisionReason,
    loadSources,
    inspectSource,
    saveSource,
    saveReview,
    setReviewSourceId,
  };
}
