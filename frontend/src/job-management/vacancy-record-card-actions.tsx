import { Archive, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

type Props = {
  archived: boolean;
  saving: boolean;
  onArchive: () => void;
  onRestore: () => void;
};

export function VacancyRecordCardActions({ archived, saving, onArchive, onRestore }: Props) {
  return (
    <Button
      type="button"
      size="sm"
      variant="outline"
      className="shrink-0"
      disabled={saving}
      onClick={archived ? onRestore : onArchive}
      aria-label={archived ? "Reinstate vacancy" : "Archive vacancy"}
    >
      {archived ? (
        <RotateCcw className="mr-1.5 h-3.5 w-3.5" />
      ) : (
        <Archive className="mr-1.5 h-3.5 w-3.5" />
      )}
      {archived ? "Reinstate" : "Archive"}
    </Button>
  );
}
