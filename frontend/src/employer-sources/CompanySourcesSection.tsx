import type { FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { EmployerSource, ExtractionRun, GreenhouseInspection } from "../api";
import { ExtractionRunHistory } from "./ExtractionRunHistory";
import { SourceRegistrationForm } from "./SourceRegistrationForm";
import { SourceReviewPanel, type SourceDecisionDraft } from "./SourceReviewPanel";

type Props = {
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

export function CompanySourcesSection(props: Props) {
  return (
    <>
      <div className="mb-3 mt-6 flex items-center justify-between gap-3 border-b border-border pb-2">
        <h4>Job sources</h4>
      </div>
      {props.sources.length ? (
        props.sources.map((source) => (
          <div className="space-y-3 border-b border-border py-4" key={source.id}>
            <div className="grid gap-3 rounded-lg border border-border bg-card p-3 sm:flex sm:items-center sm:justify-between">
              <div className="min-w-0 space-y-1">
                <strong className="text-xs font-semibold capitalize text-foreground">
                  {source.adapter_key}
                </strong>
                <a
                  href={source.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 break-all text-[10px] text-primary underline-offset-2 hover:underline"
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
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => props.onEditSource(source)}
                  >
                    Edit source
                  </Button>
                )}
              </div>
            </div>
            <SourceReviewPanel
              source={source}
              decision={props.decisions[source.id]}
              saving={props.saving}
              onChange={(field, value) => props.onDecisionChange(source, field, value)}
              onSave={() => props.onSaveDecision(source)}
            />
            <ExtractionRunHistory runs={props.extractionRuns[source.id] ?? []} />
          </div>
        ))
      ) : (
        <p className="py-4 text-xs text-muted-foreground">
          No job source registered for this company.
        </p>
      )}
      <SourceRegistrationForm
        editingSourceId={props.editingSourceId}
        sourceUrl={props.sourceUrl}
        onChangeSourceUrl={props.onChangeSourceUrl}
        onInspect={props.onInspect}
        inspection={props.inspection}
        onSaveSource={props.onSaveSource}
        onCancelEdit={props.onCancelEdit}
        inspecting={props.inspecting}
        saving={props.saving}
      />
    </>
  );
}
