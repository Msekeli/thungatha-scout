import { Button } from "@/components/ui/button";
import type { Vacancy } from "../api";
import { VacancyDescriptionPreview } from "./VacancyDescriptionPreview";
import { VacancyDetailsHeader } from "./VacancyDetailsHeader";
import { VacancyReviewActions } from "./VacancyReviewActions";

type VacancyDetailsPanelProps = {
  vacancy: Vacancy | null;
  loading: boolean;
  reviewReason: string;
  saving: boolean;
  onChangeReviewReason: (value: string) => void;
  onClear: () => void;
  onDecision: (status: Vacancy["review_status"]) => void;
  onArchive: () => void;
  onRestore: () => void;
};

export function VacancyDetailsPanel({
  vacancy, loading, reviewReason, saving, onChangeReviewReason,
  onClear, onDecision, onArchive, onRestore,
}: VacancyDetailsPanelProps) {
  if (loading) {
    return <div className="grid flex-1 place-content-center text-center text-sm text-muted-foreground">Loading vacancy…</div>;
  }
  if (!vacancy) {
    return (
      <div className="grid flex-1 place-content-center px-6 text-center">
        <p className="text-sm font-semibold text-primary">Select a vacancy record</p>
        <p className="mt-1 max-w-xs text-xs text-muted-foreground">
          Inspect extracted content and resolve records requiring admin attention.
        </p>
      </div>
    );
  }

  return (
    <>
      <VacancyDetailsHeader vacancy={vacancy} onClear={onClear} />
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        <VacancyDescriptionPreview vacancy={vacancy} />
        <VacancyReviewActions
          archived={Boolean(vacancy.archived_at)}
          reviewReason={reviewReason}
          saving={saving}
          onChangeReviewReason={onChangeReviewReason}
          onDecision={onDecision}
          onArchive={onArchive}
          onRestore={onRestore}
        />
        <details className="rounded-lg border border-border">
          <summary className="cursor-pointer px-3 py-2 text-xs font-semibold text-muted-foreground">
            Publishing payload preview
          </summary>
          <pre className="max-h-64 overflow-auto border-t bg-muted p-3 text-xs">
            {JSON.stringify({
              title: vacancy.title,
              company: vacancy.employer_name,
              location: vacancy.location_text,
              review_status: vacancy.review_status,
              review_reason: vacancy.review_reason,
              application_url: vacancy.application_url,
              source_url: vacancy.source_url,
            }, null, 2)}
          </pre>
        </details>
      </div>
    </>
  );
}
