import type { FC, FormEvent } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../components/ui/dialog";

type SourceReviewModalProps = {
  isOpen: boolean;
  onClose: () => void;
  status: string;
  onChangeStatus: (val: string) => void;
  permissionStatus: string;
  onChangePermissionStatus: (val: string) => void;
  evidenceUrl: string;
  onChangeEvidenceUrl: (val: string) => void;
  reason: string;
  onChangeReason: (val: string) => void;
  onSave: () => void;
  saving: boolean;
};

export const SourceReviewModal: FC<SourceReviewModalProps> = ({
  isOpen,
  onClose,
  status,
  onChangeStatus,
  permissionStatus,
  onChangePermissionStatus,
  evidenceUrl,
  onChangeEvidenceUrl,
  reason,
  onChangeReason,
  onSave,
  saving,
}) => {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSave();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Source Verification & Permission Review</DialogTitle>
          <DialogDescription className="text-xs text-slate-500">
            Record authoritative evidence that this source belongs to the employer.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="grid gap-3 pt-2">
          <div className="grid grid-cols-2 gap-3">
            <label>
              Source Status
              <select value={status} onChange={(e) => onChangeStatus(e.target.value)}>
                <option value="pending_verification">Pending verification</option>
                <option value="verified">Verified</option>
                <option value="temporarily_unavailable">Temporarily unavailable</option>
                <option value="invalid">Invalid</option>
                <option value="needs_review">Needs review</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
            <label>
              Permission Status
              <select
                value={permissionStatus}
                onChange={(e) => onChangePermissionStatus(e.target.value)}
              >
                <option value="unknown">Unknown</option>
                <option value="allowed">Allowed</option>
                <option value="restricted">Restricted</option>
                <option value="needs_review">Needs review</option>
              </select>
            </label>
          </div>

          <label>
            Evidence URL (Required for verified + allowed)
            <input
              type="url"
              value={evidenceUrl}
              onChange={(e) => onChangeEvidenceUrl(e.target.value)}
              placeholder="https://company.co.za/careers link to ATS"
            />
          </label>

          <label>
            Decision Reason / Notes
            <input
              type="text"
              value={reason}
              onChange={(e) => onChangeReason(e.target.value)}
              placeholder="Official careers page outbound link verified."
            />
          </label>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" className="button secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="button primary" disabled={saving}>
              {saving ? "Saving decision…" : "Save verification"}
            </button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
