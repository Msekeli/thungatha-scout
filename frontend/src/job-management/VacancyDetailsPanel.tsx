import type { Vacancy } from "../api";
import { VacancyDescriptionPreview } from "./VacancyDescriptionPreview";
import { VacancyDetailsHeader } from "./VacancyDetailsHeader";

type VacancyDetailsPanelProps = {
  vacancy: Vacancy | null;
  loading: boolean;
  saving: boolean;
  onArchive: () => void;
  onRestore: () => void;
};

export function VacancyDetailsPanel({
  vacancy,
  loading,
  saving,
  onArchive,
  onRestore,
}: VacancyDetailsPanelProps) {
  if (loading) {
    return (
      <div className="grid flex-1 place-content-center text-center text-sm text-muted-foreground">
        Loading vacancy…
      </div>
    );
  }
  if (!vacancy) {
    return (
      <div className="grid flex-1 place-content-center px-6 text-center">
        <p className="text-sm font-semibold text-primary">Select a vacancy record</p>
        <p className="mt-1 max-w-xs text-xs text-muted-foreground">
          Select a record to inspect its extracted description and source.
        </p>
      </div>
    );
  }

  return (
    <>
      <VacancyDetailsHeader
        vacancy={vacancy}
        saving={saving}
        onArchive={onArchive}
        onRestore={onRestore}
      />
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <VacancyDescriptionPreview vacancy={vacancy} />
      </div>
    </>
  );
}
