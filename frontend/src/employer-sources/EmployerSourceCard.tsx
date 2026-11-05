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
      <div className="grid gap-3 rounded-xl border border-slate-700 bg-slate-900 p-3 sm:flex sm:items-center sm:justify-between">
        <div className="min-w-0 space-y-1">
          <strong className="text-xs font-semibold capitalize text-white">
            {source.adapter_key} source
          </strong>
          {source.employer_careers_url && (
            <a
              href={source.employer_careers_url}
              target="_blank"
              rel="noreferrer"
              className="block text-xs text-cyan-300 hover:underline"
            >
              Official careers page
            </a>
          )}
          <a
            href={source.source_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 break-all text-[10px] text-slate-300 underline-offset-2 hover:text-cyan-200 hover:underline"
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
