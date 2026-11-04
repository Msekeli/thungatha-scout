import type { FC } from "react";
import type { CompanyStatus } from "../shared-contracts/employer-contracts";

type CompanyStatusActionsProps = {
  currentStatus: string;
  onUpdateStatus: (status: CompanyStatus) => void;
  onPromptDelete: () => void;
  saving: boolean;
};

export const CompanyStatusActions: FC<CompanyStatusActionsProps> = ({
  currentStatus,
  onUpdateStatus,
  onPromptDelete,
  saving,
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 py-3">
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="text-[10px] font-bold uppercase text-slate-500">
          Status:
        </span>
        <button
          type="button"
          className={`button ${
            currentStatus === "approved"
              ? "primary bg-emerald-700"
              : "secondary text-emerald-800"
          }`}
          disabled={saving}
          onClick={() => onUpdateStatus("approved")}
        >
          Approve
        </button>
        <button
          type="button"
          className={`button ${
            currentStatus === "needs_review"
              ? "primary bg-amber-700"
              : "secondary text-amber-800"
          }`}
          disabled={saving}
          onClick={() => onUpdateStatus("needs_review")}
        >
          Needs review
        </button>
        <button
          type="button"
          className={`button ${
            currentStatus === "rejected"
              ? "primary bg-red-700"
              : "secondary text-red-800"
          }`}
          disabled={saving}
          onClick={() => onUpdateStatus("rejected")}
        >
          Reject
        </button>
        <button
          type="button"
          className={`button ${
            currentStatus === "inactive"
              ? "primary bg-slate-700"
              : "secondary text-slate-600"
          }`}
          disabled={saving}
          onClick={() => onUpdateStatus("inactive")}
        >
          Deactivate
        </button>
      </div>

      <button
        type="button"
        className="button secondary text-red-700 hover:bg-red-50"
        disabled={saving}
        onClick={onPromptDelete}
      >
        Delete company
      </button>
    </div>
  );
};
