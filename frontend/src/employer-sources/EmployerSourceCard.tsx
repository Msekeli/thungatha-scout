import { ExternalLink, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { EmployerSource } from "../api";

type Props = {
  source: EmployerSource;
  saving: boolean;
  onEdit: (source: EmployerSource) => void;
};

export function EmployerSourceCard({ source, saving, onEdit }: Props) {
  return (
    <div className="scout-company-source-card">
      <div className="min-w-0">
        <p className="text-xs font-semibold capitalize scout-company-heading">
          {source.adapter_key}
        </p>
        <a
          href={source.source_url}
          target="_blank"
          rel="noreferrer"
          className="mt-1 flex items-center gap-1 break-all text-xs scout-company-link"
        >
          {source.source_url}
          <ExternalLink className="h-3 w-3 shrink-0" />
        </a>
      </div>
      {source.adapter_key === "greenhouse" && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          disabled={saving}
          onClick={() => onEdit(source)}
        >
          <Pencil className="mr-1.5 h-3.5 w-3.5" /> Edit URL
        </Button>
      )}
    </div>
  );
}
