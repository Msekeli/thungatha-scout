import { useCallback, useRef, useState } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";

type VacancyDecisionOptions = {
  selectedVacancy: Vacancy | null;
  setSelectedVacancy: (vacancy: Vacancy) => void;
  reviewReason: string;
  setReviewReason: (reason: string) => void;
  saving: boolean;
  setSaving: (saving: boolean) => void;
  onVacancyUpdated: (vacancy: Vacancy) => void;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyDecisionActions(options: VacancyDecisionOptions) {
  const {
    selectedVacancy,
    setSelectedVacancy,
    reviewReason,
    setReviewReason,
    saving,
    setSaving,
    onVacancyUpdated,
    onNotice,
    onError,
  } = options;
  const [canUndoDecision, setCanUndoDecision] = useState(false);
  const previousDecisionRef = useRef<{
    vacancyId: string;
    status: Vacancy["review_status"];
    reason: string | null;
  } | null>(null);

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
    [
      selectedVacancy,
      reviewReason,
      setSelectedVacancy,
      setSaving,
      onVacancyUpdated,
      onNotice,
      onError,
    ],
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
  }, [
    saving,
    onError,
    onVacancyUpdated,
    selectedVacancy,
    setSelectedVacancy,
    setReviewReason,
    setSaving,
    onNotice,
  ]);

  return { saveDecision, undoLastDecision, canUndoDecision };
}
