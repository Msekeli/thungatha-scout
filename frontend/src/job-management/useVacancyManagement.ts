import { useState } from "react";
import { useVacancyArchiveActions } from "./useVacancyArchiveActions";
import { useVacancySelection } from "./useVacancySelection";

type Options = {
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyManagement({ onRefresh, onNotice, onError }: Options) {
  const [savingVacancyId, setSavingVacancyId] = useState<string | null>(null);
  const selection = useVacancySelection({ onError });
  const archiveActions = useVacancyArchiveActions({
    setSavingId: setSavingVacancyId,
    onRefresh,
    onNotice,
    onError,
  });

  return { ...selection, savingVacancyId, ...archiveActions };
}
