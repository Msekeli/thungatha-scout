import { useCallback } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";

type Options = {
  setSavingId: (id: string | null) => void;
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyArchiveActions({ setSavingId, onRefresh, onNotice, onError }: Options) {
  const archive = useCallback(async (vacancy: Vacancy, reason: string): Promise<boolean> => {
    setSavingId(vacancy.id);
    onError("");
    try {
      await scoutApi.archiveVacancy(vacancy.id, reason);
      onNotice("Vacancy archived. It remains available in the Archived jobs view.");
      try {
        await onRefresh();
      } catch {
        onError("Vacancy archived, but the list could not be refreshed.");
      }
      return true;
    } catch (error) {
      onError(error instanceof Error ? error.message : "Could not archive vacancy.");
      return false;
    } finally {
      setSavingId(null);
    }
  }, [setSavingId, onRefresh, onNotice, onError]);

  const restore = useCallback(async (vacancy: Vacancy) => {
    setSavingId(vacancy.id);
    onError("");
    try {
      await scoutApi.restoreVacancy(vacancy.id);
      await onRefresh();
      onNotice("Vacancy restored to the active jobs list.");
    } catch (error) {
      onError(error instanceof Error ? error.message : "Could not restore vacancy.");
    } finally {
      setSavingId(null);
    }
  }, [setSavingId, onRefresh, onNotice, onError]);

  return { archive, restore };
}
