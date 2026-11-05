import { useCallback } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";
import type { VacancyDecisionState } from "./vacancyDecisionTypes";

type UndoDecisionOptions = {
  selectedVacancy: Vacancy | null;
  setSelectedVacancy: (vacancy: Vacancy) => void;
  setReviewReason: (reason: string) => void;
  saving: boolean;
  setSaving: (saving: boolean) => void;
  decisionState: VacancyDecisionState;
  setCanUndoDecision: (value: boolean) => void;
  onVacancyUpdated: (vacancy: Vacancy) => void;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyDecisionUndo(options: UndoDecisionOptions) {
  const {
    selectedVacancy,
    setSelectedVacancy,
    setReviewReason,
    saving,
    setSaving,
    decisionState,
    setCanUndoDecision,
    onVacancyUpdated,
    onNotice,
    onError,
  } = options;

  return useCallback(async () => {
    const previous = decisionState.current;
    if (!previous || saving) return;
    setSaving(true);
    onError("");
    try {
      const updated = await scoutApi.updateVacancyReview(
        previous.vacancyId,
        previous.status,
        previous.reason ?? "",
      );
      onVacancyUpdated(updated);
      if (selectedVacancy?.id === updated.id) {
        setSelectedVacancy(updated);
        setReviewReason(updated.review_reason ?? "");
      }
      decisionState.current = null;
      setCanUndoDecision(false);
      onNotice("Previous vacancy decision restored.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not undo the vacancy decision.");
    } finally {
      setSaving(false);
    }
  }, [
    selectedVacancy,
    setSelectedVacancy,
    setReviewReason,
    saving,
    setSaving,
    decisionState,
    setCanUndoDecision,
    onVacancyUpdated,
    onNotice,
    onError,
  ]);
}
