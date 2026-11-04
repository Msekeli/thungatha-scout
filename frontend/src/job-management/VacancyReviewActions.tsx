import type { FC, FormEvent } from "react";
import type { VacancyReviewStatus } from "../shared-contracts/vacancy-contracts";

type VacancyReviewActionsProps = {
  currentStatus: VacancyReviewStatus;
  currentReason: string;
  onSaveReview: (status: VacancyReviewStatus, reason: string) => void;
  saving: boolean;
};

export const VacancyReviewActions: FC<VacancyReviewActionsProps> = ({
  currentReason,
  onSaveReview,
  saving,
}) => {
  const handleSubmit = (status: VacancyReviewStatus, event: FormEvent) => {
    event.preventDefault();
    onSaveReview(status, currentReason);
  };

  return (
    <div className="review-actions-panel">
      <h4 className="text-xs font-bold uppercase text-slate-700">
        Review Decision
      </h4>
      <div className="review-button-group">
        <button
          type="button"
          className="button primary bg-emerald-700 hover:bg-emerald-800"
          disabled={saving}
          onClick={(event) => handleSubmit("verified", event)}
        >
          Verify (Cape Town eligible)
        </button>
        <button
          type="button"
          className="button secondary text-amber-800 border-amber-300 bg-amber-50"
          disabled={saving}
          onClick={(event) => handleSubmit("needs_verification", event)}
        >
          Needs verification
        </button>
        <button
          type="button"
          className="button secondary text-red-800 border-red-300 bg-red-50"
          disabled={saving}
          onClick={(event) => handleSubmit("rejected", event)}
        >
          Reject (Out of scope)
        </button>
      </div>
    </div>
  );
};
