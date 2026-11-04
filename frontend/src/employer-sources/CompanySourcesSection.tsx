import type { FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { EmployerSource, ExtractionRun, GreenhouseInspection } from "../api";
import { ExtractionRunHistory } from "./ExtractionRunHistory";
import { SourceRegistrationForm } from "./SourceRegistrationForm";
import { SourceReviewPanel, type SourceDecisionDraft } from "./SourceReviewPanel";

type CompanySourcesSectionProps = {
  sources: EmployerSource[];
  extractionRuns: Record<string, ExtractionRun[]>;
  decisions: Record<string, SourceDecisionDraft>;
  sourceUrl: string;
  editingSourceId: string | null;
  inspection: GreenhouseInspection | null;
  saving: boolean;
  inspecting: boolean;
  onEditSource: (source: EmployerSource) => void;
  onDecisionChange: (
    source: EmployerSource,
    field: keyof SourceDecisionDraft,
    value: string,
  ) => void;
  onSaveDecision: (source: EmployerSource) => void;
  onChangeSourceUrl: (value: string) => void;
  onInspect: () => void;
  onSaveSource: (event: FormEvent<HTMLFormElement>) => void;
  onCancelEdit: () => void;
};

export function CompanySourcesSection({
  sources,
  extractionRuns,
  decisions,
  sourceUrl,
  editingSourceId,
  inspection,
  saving,
  inspecting,
  onEditSource,
  onDecisionChange,
  onSaveDecision,
  onChangeSourceUrl,
  onInspect,
  onSaveSource,
  onCancelEdit,
}: CompanySourcesSectionProps) {
  return (
    <>
      <div className="mb-3 mt-6 flex items-center justify-between gap-3 border-b border-border pb-2">
        <h4>Job sources</h4>
      </div>
      {sources.length ? (
        sources.map((source) => {
          const runs = extractionRuns[source.id] ?? [];
          return (
            <div className="space-y-3 border-b border-border py-4" key={source.id}>
              <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-card p-3">
                <div>
                  <strong className="text-xs font-semibold capitalize text-foreground">
                    {source.adapter_key}
                  </strong>
                  <small className="block break-all text-[10px] text-muted-foreground">
                    {source.source_url}
                  </small>
                </div>
                <Badge variant="outline" className="capitalize">
                  {source.status.replaceAll("_", " ")}
                </Badge>
                {source.adapter_key === "greenhouse" && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => onEditSource(source)}
                  >
                    Edit source
                  </Button>
                )}
              </div>
              <SourceReviewPanel
                source={source}
                decision={decisions[source.id]}
                saving={saving}
                onChange={(field, value) => onDecisionChange(source, field, value)}
                onSave={() => onSaveDecision(source)}
              />
              <ExtractionRunHistory runs={runs} />
            </div>
          );
        })
      ) : (
        <p className="py-4 text-xs text-muted-foreground">
          No job source registered for this company.
        </p>
      )}
      <SourceRegistrationForm
        editingSourceId={editingSourceId}
        sourceUrl={sourceUrl}
        onChangeSourceUrl={onChangeSourceUrl}
        onInspect={onInspect}
        inspection={inspection}
        onSaveSource={onSaveSource}
        onCancelEdit={onCancelEdit}
        inspecting={inspecting}
        saving={saving}
      />
    </>
  );
}
