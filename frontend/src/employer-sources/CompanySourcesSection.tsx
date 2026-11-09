import type { FormEvent } from "react";
import type { EmployerSource, SourceInspection } from "../api";
import { SourceRegistrationForm } from "./SourceRegistrationForm";
import { EmployerSourceCard } from "./EmployerSourceCard";

type Props = {
  sources: EmployerSource[];
  sourceUrl: string;
  editingSourceId: string | null;
  inspection: SourceInspection | null;
  saving: boolean;
  inspecting: boolean;
  onEditSource: (source: EmployerSource) => void;
  onChangeSourceUrl: (value: string) => void;
  onInspect: () => void;
  onSaveSource: (event: FormEvent<HTMLFormElement>) => void;
  onCancelEdit: () => void;
};

export function CompanySourcesSection(props: Props) {
  return (
    <section className="scout-company-sources">
      <div className="mb-3 flex items-center justify-between border-b scout-company-divider pb-2">
        <h4 className="text-sm font-semibold scout-company-heading">Recruitment sources</h4>
      </div>
      {props.sources.length ? (
        <div className="grid gap-2">
          {props.sources.map((source) => (
            <EmployerSourceCard
              key={source.id}
              source={source}
              saving={props.saving}
              onEdit={props.onEditSource}
            />
          ))}
        </div>
      ) : (
        <p className="py-2 text-xs scout-company-muted">No recruitment sources added yet.</p>
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
    </section>
  );
}
