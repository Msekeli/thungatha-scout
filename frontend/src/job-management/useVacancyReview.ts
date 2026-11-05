import { useState } from "react";
import type { Vacancy } from "../api";
import { useVacancyArchiveActions } from "./useVacancyArchiveActions";
import { useVacancyDecisionActions } from "./useVacancyDecisionActions";
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
  const selection = useVacancySelection({ onError, onReasonChange: setReviewReason });
  const { selectedVacancy, setSelectedVacancy } = selection;
  const decisions = useVacancyDecisionActions({
    selectedVacancy,
    setSelectedVacancy,
    reviewReason,
    setReviewReason,
    saving,
    setSaving,
    onVacancyUpdated,
    onNotice,
    onError,
  });
  const { archive, restore } = useVacancyArchiveActions({
    selectedVacancy,
    setSaving,
    clearSelection: selection.clearSelection,
    onRefresh,
    onNotice,
    onError,
  });

  return {
    ...selection,
    reviewReason,
    setReviewReason,
    saving,
    ...decisions,
    archive,
    restore,
  };
}
