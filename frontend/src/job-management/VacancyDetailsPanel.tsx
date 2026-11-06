import type { Vacancy } from "../api";
import { VacancyDescriptionPreview } from "./VacancyDescriptionPreview";
import { VacancyDetailsHeader } from "./VacancyDetailsHeader";

type Props = { vacancy: Vacancy | null; loading: boolean };

export function VacancyDetailsPanel({ vacancy, loading }: Props) {
  if (loading) return (
    <div className="grid flex-1 place-content-center text-center text-sm text-muted-foreground">
      Loading vacancy…
    </div>
  );
  if (!vacancy) return (
    <div className="grid flex-1 place-content-center px-6 text-center">
      <p className="text-sm font-semibold text-primary">Select a vacancy record</p>
      <p className="mt-1 max-w-xs text-xs text-muted-foreground">
        Select a record to inspect its extracted description and source.
      </p>
    </div>
  );
  return (
    <>
      <VacancyDetailsHeader vacancy={vacancy} />
      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <VacancyDescriptionPreview vacancy={vacancy} />
      </div>
    </>
  );
}
