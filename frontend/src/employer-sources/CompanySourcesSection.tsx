import type { FormEvent } from "react";
import type { EmployerSource, ExtractionRun, GreenhouseInspection } from "../api";
import { SourceRegistrationForm } from "./SourceRegistrationForm";
import { EmployerSourceCard } from "./EmployerSourceCard";
import type { SourceDecisionDraft } from "./SourceReviewPanel";

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
      <div className="mb-3 mt-6 flex items-center justify-between gap-3 border-b scout-company-divider pb-2">
        <h4>Job sources</h4>
      </div>
      {props.sources.length ? (
        props.sources.map((source) => (
          <EmployerSourceCard
            key={source.id}
            source={source}
            runs={props.extractionRuns[source.id] ?? []}
            decision={props.decisions[source.id]}
            saving={props.saving}
            onEdit={props.onEditSource}
            onDecisionChange={props.onDecisionChange}
            onSaveDecision={props.onSaveDecision}
          />
        ))
      ) : (
        <p className="py-4 text-xs scout-company-muted">No job source registered for this company.</p>
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
