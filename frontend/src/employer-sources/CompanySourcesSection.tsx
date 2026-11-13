import { useState, type FormEvent } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
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
  const [addingSource, setAddingSource] = useState(false);
  const formVisible = addingSource || Boolean(props.editingSourceId);

  return (
    <section className="scout-company-sources">
      <div className="mb-3 flex items-center justify-between border-b scout-company-divider pb-2">
        <div>
          <h4 className="text-sm font-semibold text-foreground">Recruitment sources</h4>
          <p className="mt-1 text-xs text-muted-foreground">
            Register an additional careers-board URL, or edit an existing source from its card.
          </p>
        </div>
        {!formVisible && (
          <Button type="button" size="sm" variant="outline" onClick={() => setAddingSource(true)}>
            <Plus className="mr-1.5 h-3.5 w-3.5" /> Add source
          </Button>
        )}
      </div>
      {props.sources.length ? (
        <div className="grid gap-2">
          {props.sources.map((source) => (
            <EmployerSourceCard
              key={source.id}
              source={source}
              saving={props.saving}
              onEdit={(item) => {
                setAddingSource(false);
                props.onEditSource(item);
              }}
            />
          ))}
        </div>
      ) : (
        <p className="py-2 text-xs scout-company-muted">No recruitment sources added yet.</p>
      )}
      {formVisible && (
        <SourceRegistrationForm
          editingSourceId={props.editingSourceId}
          sourceUrl={props.sourceUrl}
          onChangeSourceUrl={props.onChangeSourceUrl}
          onInspect={props.onInspect}
          inspection={props.inspection}
          onSaveSource={props.onSaveSource}
          onCancelEdit={() => {
            setAddingSource(false);
            props.onCancelEdit();
          }}
          inspecting={props.inspecting}
          saving={props.saving}
        />
      )}
    </section>
  );
}
