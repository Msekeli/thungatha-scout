import { useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CompanyDeleteDialog } from "./CompanyDeleteDialog";

type Props = {
  companyName: string;
  saving: boolean;
  editing: boolean;
  onDelete: () => void;
  onEdit: () => void;
};

export function CompanyProfileActions({ companyName, saving, editing, onDelete, onEdit }: Props) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  return (
    <div className="scout-company-actions">
      <Button
        type="button"
        size="sm"
        variant="outline"
        className="scout-company-action"
        disabled={saving}
        onClick={onEdit}
      >
        <Pencil className="mr-1.5 h-3.5 w-3.5" /> {editing ? "Cancel editing" : "Edit company"}
      </Button>
      <Button
        type="button"
        size="sm"
        variant="destructive"
        className="scout-company-delete"
        disabled={saving}
        onClick={() => setDeleteOpen(true)}
      >
        <Trash2 className="mr-1.5 h-3.5 w-3.5" /> Delete company
      </Button>
      <CompanyDeleteDialog
        companyName={companyName}
        open={deleteOpen}
        saving={saving}
        onOpenChange={setDeleteOpen}
        onConfirm={onDelete}
      />
    </div>
  );
}
