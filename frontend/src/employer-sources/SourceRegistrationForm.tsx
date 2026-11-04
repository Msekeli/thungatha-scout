import type { FC, FormEvent } from "react";
import type { GreenhouseInspection } from "../shared-contracts/discovery-contracts";

type SourceRegistrationFormProps = {
  editingSourceId: string | null;
  sourceUrl: string;
  onChangeSourceUrl: (val: string) => void;
  onInspect: () => void;
  inspection: GreenhouseInspection | null;
  onSaveSource: (event: FormEvent) => void;
  onCancelEdit: () => void;
  inspecting: boolean;
  saving: boolean;
};

export const SourceRegistrationForm: FC<SourceRegistrationFormProps> = ({
  editingSourceId,
  sourceUrl,
  onChangeSourceUrl,
  onInspect,
  inspection,
  onSaveSource,
  onCancelEdit,
  inspecting,
  saving,
}) => {
  const canSave =
    !saving &&
    Boolean(inspection) &&
    inspection?.complete &&
    ["success", "empty"].includes(inspection.outcome);

  return (
    <form className="source-form" onSubmit={onSaveSource}>
      <h4>
        {editingSourceId ? "Update Greenhouse source" : "Register Greenhouse source"}
      </h4>
      <label>
        Official careers / job board URL
        <input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="https://job-boards.greenhouse.io/company"
          required
        />
      </label>
      <button
        type="button"
        className="button secondary"
        onClick={onInspect}
        disabled={inspecting || !sourceUrl.trim()}
      >
        {inspecting ? "Checking source…" : "Check Greenhouse source"}
      </button>

      {inspection && (
        <div className="inspection-preview">
          <strong>{inspection.board_name || inspection.board_token}</strong>
          <span>
            {inspection.outcome} · {inspection.jobs.length} sample jobs
          </span>
          {inspection.detail && <small>{inspection.detail}</small>}
        </div>
      )}

      <div className="form-actions">
        {editingSourceId && (
          <button type="button" className="button secondary" onClick={onCancelEdit}>
            Cancel edit
          </button>
        )}
        <button className="button primary" disabled={!canSave}>
          {saving ? "Saving…" : editingSourceId ? "Update source" : "Save source"}
        </button>
      </div>
    </form>
  );
};
