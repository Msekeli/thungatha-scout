import { useCallback, useRef, useState } from "react";
import { scoutApi } from "../api";
import type { Vacancy } from "../api";

type UseVacancySelectionOptions = {
  onError: (message: string) => void;
  onReasonChange: (reason: string) => void;
};

export function useVacancySelection({ onError, onReasonChange }: UseVacancySelectionOptions) {
  const [selectedVacancy, setSelectedVacancy] = useState<Vacancy | null>(null);
  const [selectedVacancyId, setSelectedVacancyId] = useState<string | null>(null);
  const [openingVacancyId, setOpeningVacancyId] = useState<string | null>(null);
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
        onReasonChange(completeVacancy.review_reason ?? "");
      } catch (reason) {
        if (requestId !== requestRef.current) return;
        onError(reason instanceof Error ? reason.message : "Could not load vacancy details.");
        setSelectedVacancyId(null);
      } finally {
        if (requestId === requestRef.current) setOpeningVacancyId(null);
      }
    },
    [onError, onReasonChange],
  );

  return {
    selectedVacancy,
    setSelectedVacancy,
    selectedVacancyId,
    openingVacancyId,
    openVacancy,
    clearSelection,
  };
}
