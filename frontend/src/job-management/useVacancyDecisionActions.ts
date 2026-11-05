import { useRef, useState } from "react";
import type { Vacancy } from "../api";
import { useVacancyDecisionSave } from "./useVacancyDecisionSave";
import { useVacancyDecisionUndo } from "./useVacancyDecisionUndo";
import type { VacancyDecisionState } from "./vacancyDecisionTypes";

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
  const [canUndoDecision, setCanUndoDecision] = useState(false);
  const decisionState = useRef<VacancyDecisionState["current"]>(null);
  const saveDecision = useVacancyDecisionSave({
    ...options, decisionState, setCanUndoDecision,
  });
  const undoLastDecision = useVacancyDecisionUndo({
    ...options, decisionState, setCanUndoDecision,
  });

  return { saveDecision, undoLastDecision, canUndoDecision };
}
