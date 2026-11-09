import type { FC } from "react";
import { Button } from "@/components/ui/button";
import type { EmployerSource } from "../shared-contracts/employer-contracts";

type EmployerSourceItemProps = {
  source: EmployerSource;
  onEditSource: (source: EmployerSource) => void;
};

export const EmployerSourceItem: FC<EmployerSourceItemProps> = ({ source, onEditSource }) => (
  <div className="grid gap-3 rounded-lg border border-border bg-card p-3 sm:flex sm:items-center sm:justify-between">
    <div className="min-w-0 space-y-1">
      <strong className="text-sm font-semibold text-foreground">{source.adapter_key}</strong>
      <p className="break-all text-xs text-muted-foreground">{source.source_url}</p>
    </div>
    <Button type="button" size="sm" variant="outline" onClick={() => onEditSource(source)}>
      Edit source
    </Button>
  </div>
);
