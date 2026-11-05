import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { EmployerSource, ExtractionRun } from "../api";
import { ExtractionRunHistory } from "./ExtractionRunHistory";
import { SourceReviewPanel, type SourceDecisionDraft } from "./SourceReviewPanel";

type Props = {
  source: EmployerSource;
  runs: ExtractionRun[];
  decision: SourceDecisionDraft;
  saving: boolean;
  onEdit: (source: EmployerSource) => void;
  onDecisionChange: (
    source: EmployerSource,
    field: keyof SourceDecisionDraft,
    value: string,
  ) => void;
  onSaveDecision: (source: EmployerSource) => void;
};

export function EmployerSourceCard({
  source,
  runs,
  decision,
  saving,
  onEdit,
  onDecisionChange,
  onSaveDecision,
}: Props) {
  return (
    <div className="space-y-3 border-b border-border py-4">
      <div className="scout-company-source-card">
        <div className="min-w-0 space-y-1">
          <strong className="text-xs font-semibold capitalize scout-company-heading">
            {source.adapter_key} source
          </strong>
          {source.employer_careers_url && (
            <a
              href={source.employer_careers_url}
              target="_blank"
              rel="noreferrer"
              className="scout-company-link"
            >
              Official careers page · {source.employer_careers_url.replace(/^https?:\/\//, "")}
            </a>
          )}
          <a
            href={source.source_url}
            target="_blank"
            rel="noreferrer"
            className="scout-company-link break-all text-[10px]"
          >
            {source.source_url}
          </a>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="capitalize">
            {source.status.replaceAll("_", " ")}
          </Badge>
          <Badge variant="secondary" className="capitalize">
            {source.permission_status.replaceAll("_", " ")}
          </Badge>
          {source.adapter_key === "greenhouse" && (
            <Button type="button" variant="outline" size="sm" onClick={() => onEdit(source)}>
              Edit source
            </Button>
          )}
        </div>
      </div>
      <SourceReviewPanel
        source={source}
        decision={decision}
        saving={saving}
        onChange={(field, value) => onDecisionChange(source, field, value)}
        onSave={() => onSaveDecision(source)}
      />
      <ExtractionRunHistory runs={runs} />
    </div>
  );
}
