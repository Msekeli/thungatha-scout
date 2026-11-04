import type { FC } from "react";
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
          <span className="review-state text-[9px]">{source.status.replace("_", " ")}</span>
          <span className="review-state text-[9px] bg-slate-100 text-slate-600">
            {source.permission_status}
          </span>
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
