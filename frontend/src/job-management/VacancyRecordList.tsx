import { useState } from "react";
import type { Vacancy } from "../api";
import { VacancyArchiveDialog } from "./VacancyArchiveDialog";
import { VacancyRecordCard } from "./VacancyRecordCard";

type Props = {
  vacancies: Vacancy[];
  loading: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  onLoadMore: () => Promise<void>;
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  savingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string) => void;
  onArchive: (vacancy: Vacancy, reason: string) => Promise<boolean>;
  onRestore: (vacancy: Vacancy) => void;
};

export function VacancyRecordList(props: Props) {
  const [archiveTarget, setArchiveTarget] = useState<Vacancy | null>(null);
  const { vacancies, loading, loadingMore, hasMore, onLoadMore } = props;
  return (
    <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3" onScroll={(event) => {
      const element = event.currentTarget;
      if (element.scrollHeight - element.scrollTop - element.clientHeight < 180) void onLoadMore();
    }}>
      {loading && vacancies.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">Loading vacancies…</p>
      ) : vacancies.length === 0 ? (
        <div className="py-12 text-center">
          <p className="text-sm font-semibold">No matching records</p>
          <p className="mt-1 text-xs text-muted-foreground">Adjust the filters or register a source.</p>
        </div>
      ) : vacancies.map((vacancy) => (
        <VacancyRecordCard key={vacancy.id} vacancy={vacancy}
          selected={props.selectedVacancyId === vacancy.id}
          opening={props.openingVacancyId === vacancy.id}
          saving={props.savingVacancyId === vacancy.id}
          onOpen={() => props.onOpenVacancy(vacancy.id)}
          onArchive={() => setArchiveTarget(vacancy)}
          onRestore={() => props.onRestore(vacancy)} />
      ))}
      {!loading && hasMore && (
        <div className="py-3 text-center text-xs text-muted-foreground" aria-live="polite">
          {loadingMore ? "Loading more vacancies…" : "Scroll to load more"}
        </div>
      )}
      <VacancyArchiveDialog vacancy={archiveTarget} open={Boolean(archiveTarget)}
        saving={props.savingVacancyId === archiveTarget?.id}
        onOpenChange={(open) => { if (!open) setArchiveTarget(null); }}
        onConfirm={(reason) => archiveTarget
          ? props.onArchive(archiveTarget, reason) : Promise.resolve(false)} />
    </div>
  );
}
