import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";

type CompanyStatus = "approved" | "needs_review" | "rejected" | "inactive";
type Props = { currentStatus: string; saving: boolean; onUpdateStatus: (status: CompanyStatus) => void; onDelete: () => void; onEdit: () => void };

export function CompanyProfileActions({ currentStatus, saving, onUpdateStatus, onDelete, onEdit }: Props) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  return (
    <div className="flex flex-wrap gap-2 border-b border-border pb-4">
      <Button type="button" size="sm" variant="outline" disabled={saving} onClick={onEdit}><Pencil className="mr-1.5 h-3.5 w-3.5" />Edit company</Button>
      {currentStatus !== "approved" && <Button type="button" size="sm" disabled={saving} onClick={() => onUpdateStatus("approved")}>Approve</Button>}
      {currentStatus !== "needs_review" && <Button type="button" size="sm" variant="outline" disabled={saving} onClick={() => onUpdateStatus("needs_review")}>Flag for review</Button>}
      {currentStatus !== "rejected" && <Button type="button" size="sm" variant="outline" disabled={saving} onClick={() => onUpdateStatus("rejected")}>Reject</Button>}
      {currentStatus !== "inactive" && <Button type="button" size="sm" variant="outline" disabled={saving} onClick={() => onUpdateStatus("inactive")}>Deactivate</Button>}
      <Button type="button" size="sm" variant="destructive" className="ml-auto" disabled={saving} onClick={() => setDeleteOpen(true)}><Trash2 className="mr-1.5 h-3.5 w-3.5" />Delete</Button>
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Permanently delete company?</DialogTitle><DialogDescription>This action cannot be undone. Companies with linked sources or vacancies are currently protected by the backend and cannot yet be deleted.</DialogDescription></DialogHeader>
          <div className="flex justify-end gap-2 pt-3">
            <Button type="button" variant="outline" onClick={() => setDeleteOpen(false)} disabled={saving}>Cancel</Button>
            <Button type="button" variant="destructive" disabled={saving} onClick={() => { onDelete(); setDeleteOpen(false); }}>{saving ? "Deleting…" : "Delete permanently"}</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
