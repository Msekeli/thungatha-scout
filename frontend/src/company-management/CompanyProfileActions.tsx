import { Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

type CompanyStatus = "approved" | "needs_review" | "rejected" | "inactive";

type CompanyProfileActionsProps = {
  currentStatus: string;
  saving: boolean;
  onUpdateStatus: (status: CompanyStatus) => void;
  onDelete: () => void;
};

export function CompanyProfileActions({
  currentStatus,
  saving,
  onUpdateStatus,
  onDelete,
}: CompanyProfileActionsProps) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-border pb-4">
      {currentStatus !== "approved" && (
        <Button
          type="button"
          size="sm"
          disabled={saving}
          onClick={() => onUpdateStatus("approved")}
        >
          Approve company
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
          Reject company
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
        onClick={onDelete}
      >
        <Trash2 className="h-3.5 w-3.5" />
        Delete
      </Button>
    </div>
  );
}
