import { Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CompanyDeleteDialog } from "./CompanyDeleteDialog";
import { useState } from "react";

type CompanyStatus = "approved" | "needs_review" | "rejected" | "inactive";
type Props = {
  currentStatus: string;
  saving: boolean;
  onUpdateStatus: (status: CompanyStatus) => void;
  onDelete: () => void;
  onEdit: () => void;
};

export function CompanyProfileActions({
  currentStatus,
  saving,
  onUpdateStatus,
  onDelete,
  onEdit,
}: Props) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  return (
    <div className="flex flex-wrap gap-2 border-b border-border pb-4">
      <Button type="button" size="sm" variant="outline" disabled={saving} onClick={onEdit}>
        <Pencil className="mr-1.5 h-3.5 w-3.5" />
        Edit company
      </Button>
      {currentStatus !== "approved" && (
        <Button
          type="button"
          size="sm"
          disabled={saving}
          onClick={() => onUpdateStatus("approved")}
        >
          Approve
        </Button>
      )}
      {currentStatus !== "needs_review" && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={saving}
          onClick={() => onUpdateStatus("needs_review")}
        >
          Flag for review
        </Button>
      )}
      {currentStatus !== "rejected" && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={saving}
          onClick={() => onUpdateStatus("rejected")}
        >
          Reject
        </Button>
      )}
      {currentStatus !== "inactive" && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={saving}
          onClick={() => onUpdateStatus("inactive")}
        >
          Deactivate
        </Button>
      )}
      <Button
        type="button"
        size="sm"
        variant="destructive"
        className="ml-auto"
        disabled={saving}
        onClick={() => setDeleteOpen(true)}
      >
        <Trash2 className="mr-1.5 h-3.5 w-3.5" />
        Delete
      </Button>
      <CompanyDeleteDialog
        open={deleteOpen}
        saving={saving}
        onOpenChange={setDeleteOpen}
        onConfirm={() => {
          onDelete();
          setDeleteOpen(false);
        }}
      />
    </div>
  );
}
