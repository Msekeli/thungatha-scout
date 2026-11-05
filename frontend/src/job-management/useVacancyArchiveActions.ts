import { useCallback } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";

type UseVacancyArchiveActionsOptions = {
  selectedVacancy: Vacancy | null;
  setSaving: (saving: boolean) => void;
  clearSelection: () => void;
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyArchiveActions({
  selectedVacancy,
  setSaving,
  clearSelection,
  onRefresh,
  onNotice,
  onError,
}: UseVacancyArchiveActionsOptions) {
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
  }, [selectedVacancy, setSaving, clearSelection, onRefresh, onNotice, onError]);

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
  }, [selectedVacancy, setSaving, clearSelection, onRefresh, onNotice, onError]);

  return { archive, restore };
}
