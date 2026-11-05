import { useCallback } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";
import type { VacancyDecisionState, PreviousVacancyDecision } from "./vacancyDecisionTypes";

type SaveDecisionOptions = {
  selectedVacancy: Vacancy | null;
  reviewReason: string;
  setSaving: (saving: boolean) => void;
  decisionState: VacancyDecisionState;
  setCanUndoDecision: (value: boolean) => void;
  setSelectedVacancy: (vacancy: Vacancy) => void;
  onVacancyUpdated: (vacancy: Vacancy) => void;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyDecisionSave(options: SaveDecisionOptions) {
  const {
    selectedVacancy,
    reviewReason,
    setSaving,
    decisionState,
    setCanUndoDecision,
    setSelectedVacancy,
    onVacancyUpdated,
    onNotice,
    onError,
  } = options;

  return useCallback(
    async (status: Vacancy["review_status"]) => {
      if (!selectedVacancy) return;
      setSaving(true);
      onError("");
      try {
        const previous: PreviousVacancyDecision = {
          vacancyId: selectedVacancy.id,
          status: selectedVacancy.review_status,
          reason: selectedVacancy.review_reason ?? null,
        };
        const updated = await scoutApi.updateVacancyReview(
          selectedVacancy.id,
          status,
          reviewReason,
        );
        decisionState.current = previous;
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
      setSaving,
      decisionState,
      setCanUndoDecision,
      setSelectedVacancy,
      onVacancyUpdated,
      onNotice,
      onError,
    ],
  );
}
