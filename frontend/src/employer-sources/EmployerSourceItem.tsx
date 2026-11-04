import type { FC } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { EmployerSource } from "../shared-contracts/employer-contracts";

type EmployerSourceItemProps = {
  source: EmployerSource;
  onEditSource: (source: EmployerSource) => void;
  onOpenReview: (source: EmployerSource) => void;
};

export const EmployerSourceItem: FC<EmployerSourceItemProps> = ({
  source,
  onEditSource,
  onOpenReview,
}) => {
  return (
    <div className="grid gap-3 rounded-lg border border-border bg-card p-3 sm:flex sm:items-center sm:justify-between">
      <div className="min-w-0 space-y-1">
        <div className="flex flex-wrap items-center gap-2">
          <strong className="text-sm font-semibold text-foreground">{source.adapter_key}</strong>
          <Badge variant="outline" className="text-[9px] uppercase tracking-wide">
            {source.status.replace("_", " ")}
          </Badge>
          <Badge variant="secondary" className="text-[9px]">
            {source.permission_status}
          </Badge>
        </div>
        <p className="break-all text-xs text-muted-foreground">{source.source_url}</p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <Button type="button" size="sm" variant="outline" onClick={() => onOpenReview(source)}>
          Verify source
        </Button>
        {source.adapter_key === "greenhouse" && (
          <Button type="button" size="sm" variant="outline" onClick={() => onEditSource(source)}>
            Edit
          </Button>
        )}
      </div>
    </div>
  );
};
