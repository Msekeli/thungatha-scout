import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type Props = {
  companyName: string;
  open: boolean;
  saving: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
};

export function CompanyDeleteDialog({ companyName, open, saving, onOpenChange, onConfirm }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="scout-company-delete-dialog max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" /> Permanently delete company?
          </DialogTitle>
          <DialogDescription>
            You are deleting <strong className="scout-company-heading">{companyName}</strong>. This
            permanently removes the company, its registered sources, extraction history and all
            collected vacancies from Scout. This cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-end gap-2 pt-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button type="button" variant="destructive" disabled={saving} onClick={onConfirm}>
            {saving ? "Deleting…" : "Delete company and jobs"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
