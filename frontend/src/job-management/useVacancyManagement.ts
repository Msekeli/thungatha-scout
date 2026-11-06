import { useState } from "react";
import { useVacancyArchiveActions } from "./useVacancyArchiveActions";
import { useVacancySelection } from "./useVacancySelection";

type UseVacancyManagementOptions = {
  onRefresh: () => Promise<void>;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useVacancyManagement({
  onRefresh,
  onNotice,
  onError,
}: UseVacancyManagementOptions) {
  const [saving, setSaving] = useState(false);
  const selection = useVacancySelection({ onError });
  const archiveActions = useVacancyArchiveActions({
    selectedVacancy: selection.selectedVacancy,
    setSaving,
    clearSelection: selection.clearSelection,
    onRefresh,
    onNotice,
    onError,
  });

  return {
    ...selection,
    saving,
    ...archiveActions,
  };
}
