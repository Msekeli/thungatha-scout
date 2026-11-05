import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";

type Props = {
  companyName: string;
  open: boolean;
  saving: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
};

export function CompanyDeleteDialog({
  companyName, open, saving, onOpenChange, onConfirm,
}: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md border-destructive/40">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" /> Permanently delete company?
          </DialogTitle>
          <DialogDescription>
            You are deleting <strong className="text-foreground">{companyName}</strong>.
            This permanently removes the company, its job boards, extraction history and
            collected vacancies from Scout. You cannot undo this; the company must be
            registered again manually if deleted by mistake.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-end gap-2 pt-3">
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}
            disabled={saving}>Cancel</Button>
          <Button type="button" variant="destructive" disabled={saving} onClick={onConfirm}>
            {saving ? "Deleting…" : "Delete permanently"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
