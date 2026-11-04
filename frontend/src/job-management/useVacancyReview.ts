import { useCallback, useRef, useState } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";

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
  const [selectedVacancy, setSelectedVacancy] = useState<Vacancy | null>(null);
  const [selectedVacancyId, setSelectedVacancyId] = useState<string | null>(null);
  const [openingVacancyId, setOpeningVacancyId] = useState<string | null>(null);
  const [reviewReason, setReviewReason] = useState("");
  const [saving, setSaving] = useState(false);
  const [canUndoDecision, setCanUndoDecision] = useState(false);
  const previousDecisionRef = useRef<{
    vacancyId: string;
    status: Vacancy["review_status"];
    reason: string | null;
  } | null>(null);
  const requestRef = useRef(0);

  const clearSelection = useCallback(() => {
    requestRef.current += 1;
    setSelectedVacancy(null);
    setSelectedVacancyId(null);
    setOpeningVacancyId(null);
  }, []);

  const openVacancy = useCallback(
    async (vacancyId: string, visibleVacancies: Vacancy[]) => {
      const requestId = ++requestRef.current;
      onError("");
      setSelectedVacancyId(vacancyId);
      setOpeningVacancyId(vacancyId);
      setSelectedVacancy(null);
      try {
        const vacancy = await scoutApi.getVacancy(vacancyId);
        if (requestId !== requestRef.current) return;
        const listRecord = visibleVacancies.find((item) => item.id === vacancyId);
        const completeVacancy = {
          ...vacancy,
          description: vacancy.description ?? listRecord?.description ?? null,
        };
        setSelectedVacancy(completeVacancy);
        setReviewReason(completeVacancy.review_reason ?? "");
      } catch (reason) {
        if (requestId !== requestRef.current) return;
        onError(reason instanceof Error ? reason.message : "Could not load vacancy details.");
        setSelectedVacancyId(null);
      } finally {
        if (requestId === requestRef.current) setOpeningVacancyId(null);
      }
    },
    [onError],
  );

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
    [selectedVacancy, reviewReason, onVacancyUpdated, onNotice, onError],
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
  }, [saving, onError, onVacancyUpdated, selectedVacancy, onNotice]);

  const archive = useCallback(async () => {
    if (!selectedVacancy) return;
    const reason = window.prompt("Why are you archiving this vacancy?") ?? "";
    if (!reason.trim()) return;
    setSaving(true);
    onError("");
    try {
      await scoutApi.archiveVacancy(selectedVacancy.id, reason);
      clearSelection();
      await onRefresh();
      onNotice("Vacancy archived. It remains available in the Archived jobs view.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not archive vacancy.");
    } finally {
      setSaving(false);
    }
  }, [selectedVacancy, clearSelection, onRefresh, onNotice, onError]);

  const restore = useCallback(async () => {
    if (!selectedVacancy) return;
    setSaving(true);
    onError("");
    try {
      await scoutApi.restoreVacancy(selectedVacancy.id);
      clearSelection();
      await onRefresh();
      onNotice("Vacancy restored to the active jobs list.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not restore vacancy.");
    } finally {
      setSaving(false);
    }
  }, [selectedVacancy, clearSelection, onRefresh, onNotice, onError]);

  return {
    selectedVacancy,
    selectedVacancyId,
    openingVacancyId,
    reviewReason,
    setReviewReason,
    saving,
    openVacancy,
    saveDecision,
    undoLastDecision,
    canUndoDecision,
    archive,
    restore,
    clearSelection,
  };
}
