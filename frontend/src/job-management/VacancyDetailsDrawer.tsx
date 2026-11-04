import type { FC } from "react";
import type { Vacancy } from "../shared-contracts/vacancy-contracts";
import { decodeGreenhouseContent } from "./html-content-decoder";
import { VacancyReviewActions } from "./VacancyReviewActions";
import { VacancyArchiveActions } from "./VacancyArchiveActions";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "../components/ui/sheet";

type VacancyDetailsDrawerProps = {
  vacancy: Vacancy | null;
  isOpen: boolean;
  onClose: () => void;
  reviewReason: string;
  onChangeReviewReason: (value: string) => void;
  onSaveReview: (status: Vacancy["review_status"], reason: string) => void;
  onArchive: () => void;
  onRestore: () => void;
  saving: boolean;
};

export const VacancyDetailsDrawer: FC<VacancyDetailsDrawerProps> = ({
  vacancy,
  isOpen,
  onClose,
  reviewReason,
  onChangeReviewReason,
  onSaveReview,
  onArchive,
  onRestore,
  saving,
}) => {
  if (!vacancy) return null;

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:max-w-xl overflow-y-auto">
        <SheetHeader>
          <div className="flex items-center gap-2">
            <span className={`review-state ${vacancy.review_status}`}>
              {vacancy.review_status.replace("_", " ")}
            </span>
            <span className="text-xs text-slate-500">{vacancy.employer_name}</span>
          </div>
          <SheetTitle className="text-lg font-bold">{vacancy.title}</SheetTitle>
          <SheetDescription className="text-xs text-slate-500">
            {vacancy.location_text || "Location not specified"}
          </SheetDescription>
        </SheetHeader>

        <div className="vacancy-drawer-body">
          <div className="vacancy-meta-grid">
            <div className="vacancy-meta-item">
              <span>Department</span>
              <strong>{vacancy.department || "General"}</strong>
            </div>
            <div className="vacancy-meta-item">
              <span>Application link</span>
              <a
                href={vacancy.application_url}
                target="_blank"
                rel="noreferrer"
                className="text-cyan-800 underline text-xs font-semibold truncate"
              >
                External post ↗
              </a>
            </div>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-700">
              Review notes & justification
              <input
                type="text"
                value={reviewReason}
                onChange={(event) => onChangeReviewReason(event.target.value)}
                placeholder="e.g. Cape Town office confirmed"
              />
            </label>
          </div>

          <VacancyReviewActions
            currentStatus={vacancy.review_status}
            currentReason={reviewReason}
            onSaveReview={onSaveReview}
            saving={saving}
          />

          <VacancyArchiveActions
            isArchived={Boolean(vacancy.archived_at)}
            reason={reviewReason}
            onChangeReason={onChangeReviewReason}
            onArchive={onArchive}
            onRestore={onRestore}
            saving={saving}
          />

          {vacancy.description && (
            <div className="grid gap-2">
              <span className="text-xs font-bold text-slate-700">Job Description</span>
              <div
                className="vacancy-description"
                dangerouslySetInnerHTML={{
                  __html: decodeGreenhouseContent(vacancy.description),
                }}
              />
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
};
