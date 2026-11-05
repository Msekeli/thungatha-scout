import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ShieldCheck } from "lucide-react";
import type { Vacancy } from "../api";

type VacancyReviewActionsProps = {
  archived: boolean;
  reviewReason: string;
  saving: boolean;
  onChangeReviewReason: (value: string) => void;
  onDecision: (status: Vacancy["review_status"]) => void;
  onArchive: () => void;
  onRestore: () => void;
};

export function VacancyReviewActions({
  archived,
  reviewReason,
  saving,
  onChangeReviewReason,
  onDecision,
  onArchive,
  onRestore,
}: VacancyReviewActionsProps) {
  return (
    <section className="rounded-lg border border-border">
      <div className="border-b bg-muted px-3 py-2">
        <h4 className="text-xs font-bold text-primary">Admin review actions</h4>
        <p className="mt-1 text-[10px] text-muted-foreground">
          Pending is the database default; it does not mean automated verification has run.
        </p>
      </div>
      <div className="space-y-3 p-3">
        <label className="grid gap-1 text-xs font-medium text-muted-foreground">
          Decision notes
          <Textarea
            value={reviewReason}
            disabled={archived}
            onChange={(event) => onChangeReviewReason(event.target.value)}
            placeholder="Record the reason for your decision"
            aria-label="Vacancy decision notes"
          />
        </label>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            size="sm"
            variant="ghost"
            disabled={saving || archived}
            onClick={() => onDecision("verified")}
            className="bg-success text-white shadow-sm hover:brightness-95"
          >
            <ShieldCheck className="h-4 w-4" />
            Mark verified
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={saving || archived}
            onClick={() => onDecision("needs_verification")}
          >
            Needs verification
          </Button>
          <Button
            type="button"
            size="sm"
            variant="destructive"
            disabled={saving || archived}
            onClick={() => onDecision("rejected")}
          >
            Reject record
          </Button>
          {archived ? (
            <Button type="button" size="sm" disabled={saving} onClick={onRestore}>
              Restore
            </Button>
          ) : (
            <Button
              type="button"
              size="sm"
              variant="outline"
              disabled={saving}
              onClick={onArchive}
            >
              Archive
            </Button>
          )}
        </div>
      </div>
    </section>
  );
}
