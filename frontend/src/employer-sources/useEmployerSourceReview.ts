import { useState } from "react";
import { scoutApi } from "../api";
import type { EmployerSource } from "../api";

type SourceReviewDecision = {
  status: string;
  permission_status: string;
  evidence_url: string;
  reason: string;
};

type DecisionField = keyof SourceReviewDecision;

type UseEmployerSourceReviewOptions = {
  employerId: string | null;
  onSourceUpdated: (source: EmployerSource) => void;
  onDashboardSourceUpdated: (source: EmployerSource) => void;
  setSaving: (saving: boolean) => void;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useEmployerSourceReview({
  employerId,
  onSourceUpdated,
  onDashboardSourceUpdated,
  setSaving,
  onNotice,
  onError,
}: UseEmployerSourceReviewOptions) {
  const [decisions, setDecisions] = useState<Record<string, SourceReviewDecision>>({});

  function updateField(source: EmployerSource, field: DecisionField, value: string) {
    setDecisions((current) => {
      const existing = current[source.id] ?? {
        status: source.status,
        permission_status: source.permission_status,
        evidence_url: "",
        reason: "",
      };

      return {
        ...current,
        [source.id]: { ...existing, [field]: value },
      };
    });
  }

  async function saveDecision(source: EmployerSource) {
    if (!employerId) return;

    const decision = decisions[source.id] ?? {
      status: source.status,
      permission_status: source.permission_status,
      evidence_url: "",
      reason: "",
    };

    if (
      decision.status === "verified" &&
      decision.permission_status === "allowed" &&
      !decision.evidence_url.trim()
    ) {
      onError("Add an evidence URL before verifying and permitting this source.");
      return;
    }

    setSaving(true);
    onError("");
    onNotice("");

    try {
      const updated = await scoutApi.updateSourceReview(employerId, source.id, decision);
      onSourceUpdated(updated);
      onDashboardSourceUpdated(updated);
      onNotice("Source verification and permission decision saved.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not update source decision.");
    } finally {
      setSaving(false);
    }
  }

  return { decisions, updateField, saveDecision };
}
