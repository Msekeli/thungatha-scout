import { useCallback, useRef, useState } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";
import { useVacancyArchiveActions } from "./useVacancyArchiveActions";
import { useVacancySelection } from "./useVacancySelection";

type UseVacancyReviewOptions = {
  onVacancyUpdated: (vacancy: Vacancy) => void;
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyReview({
  onVacancyUpdated,
  onRefresh,
  onNotice,
  onError,
}: UseVacancyReviewOptions) {
  const [reviewReason, setReviewReason] = useState("");
  const [saving, setSaving] = useState(false);
  const [canUndoDecision, setCanUndoDecision] = useState(false);
  const previousDecisionRef = useRef<{
    vacancyId: string;
    status: Vacancy["review_status"];
    reason: string | null;
  } | null>(null);
  const selection = useVacancySelection({ onError, onReasonChange: setReviewReason });
  const { selectedVacancy, setSelectedVacancy } = selection;
  const { archive, restore } = useVacancyArchiveActions({
    selectedVacancy,
    setSaving,
    clearSelection: selection.clearSelection,
    onRefresh,
    onNotice,
    onError,
  });

  const saveDecision = useCallback(
    async (status: Vacancy["review_status"]) => {
      if (!selectedVacancy) return;
      setSaving(true);
      onError("");
      try {
        const previousDecision = {
          vacancyId: selectedVacancy.id,
          status: selectedVacancy.review_status,
          reason: selectedVacancy.review_reason ?? null,
        };
        const updated = await scoutApi.updateVacancyReview(
          selectedVacancy.id,
          status,
          reviewReason,
        );
        previousDecisionRef.current = previousDecision;
        setCanUndoDecision(true);
        setSelectedVacancy(updated);
        onVacancyUpdated(updated);
        onNotice(`Vacancy marked ${status.replaceAll("_", " ")}.`);
      } catch (reason) {
        onError(reason instanceof Error ? reason.message : "Could not save the vacancy decision.");
      } finally {
        setSaving(false);
      }
    },
    [selectedVacancy, reviewReason, setSelectedVacancy, onVacancyUpdated, onNotice, onError],
  );

  const undoLastDecision = useCallback(async () => {
    const previousDecision = previousDecisionRef.current;
    if (!previousDecision || saving) return;
    setSaving(true);
    onError("");
    try {
      const updated = await scoutApi.updateVacancyReview(
        previousDecision.vacancyId,
        previousDecision.status,
        previousDecision.reason ?? "",
      );
      onVacancyUpdated(updated);
      if (selectedVacancy?.id === updated.id) {
        setSelectedVacancy(updated);
        setReviewReason(updated.review_reason ?? "");
      }
      previousDecisionRef.current = null;
      setCanUndoDecision(false);
      onNotice("Previous vacancy decision restored.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not undo the vacancy decision.");
    } finally {
      setSaving(false);
    }
  }, [saving, onError, onVacancyUpdated, selectedVacancy, setSelectedVacancy, onNotice]);

  return {
    ...selection,
    reviewReason,
    setReviewReason,
    saving,
    saveDecision,
    undoLastDecision,
    canUndoDecision,
    archive,
    restore,
  };
}
