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
    <div className="source-item">
      <div>
        <div className="flex items-center gap-2">
          <strong>{source.adapter_key}</strong>
          <Badge variant="outline" className="text-[9px] uppercase tracking-wide">
            {source.status.replace("_", " ")}
          </Badge>
          <Badge variant="secondary" className="text-[9px]">
            {source.permission_status}
          </Badge>
        </div>
        <small>{source.source_url}</small>
      </div>
      <div className="flex items-center gap-2">
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
