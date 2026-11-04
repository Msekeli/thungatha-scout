import type { FC } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../components/ui/dialog";

type CompanyDeletionDialogProps = {
  isOpen: boolean;
  onClose: () => void;
  companyName: string;
  onConfirmDelete: () => void;
  deleting: boolean;
};

export const CompanyDeletionDialog: FC<CompanyDeletionDialogProps> = ({
  isOpen,
  onClose,
  companyName,
  onConfirmDelete,
  deleting,
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-red-700">Delete Company</DialogTitle>
          <DialogDescription className="text-xs text-slate-600">
            Are you sure you want to delete <strong>{companyName}</strong>? Companies with
            registered sources or historical vacancies cannot be deleted and should be marked
            inactive instead.
          </DialogDescription>
        </DialogHeader>

        <div className="flex justify-end gap-2 pt-3">
          <button type="button" className="button secondary" onClick={onClose} disabled={deleting}>
            Cancel
          </button>
          <button
            type="button"
            className="button primary bg-red-700 hover:bg-red-800"
            onClick={onConfirmDelete}
            disabled={deleting}
          >
            {deleting ? "Deleting…" : "Confirm Delete"}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
