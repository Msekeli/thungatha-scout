import type { FC, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { SourceInspection } from "../api";

type SourceRegistrationFormProps = {
  editingSourceId: string | null;
  sourceUrl: string;
  onChangeSourceUrl: (value: string) => void;
  onInspect: () => void;
  inspection: SourceInspection | null;
  onSaveSource: (event: FormEvent<HTMLFormElement>) => void;
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
    <form className="scout-company-form-section mt-5" onSubmit={onSaveSource}>
      <h4 className="text-sm font-semibold scout-company-heading">
        {editingSourceId ? "Update recruitment source" : "Register recruitment source"}
      </h4>
      <label className="grid gap-1 text-xs font-medium scout-company-muted">
        Official careers / job board URL
        <Input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="Paste an official careers or ATS board URL"
          className="scout-company-field"
          required
        />
      </label>
      <Button
        type="button"
        size="sm"
        variant="outline"
        className="w-fit"
        onClick={onInspect}
        disabled={inspecting || !sourceUrl.trim()}
      >
        {inspecting ? "Checking source…" : "Check source"}
      </Button>
      {inspection && (
        <div className="grid gap-1 rounded-lg border border-border bg-card p-3 text-xs">
          <strong className="scout-company-heading">
            {inspection.board_name || inspection.board_token}
          </strong>
          <span className="scout-company-muted">
            {inspection.outcome} · {inspection.jobs.length} sample jobs
          </span>
          {inspection.detail && <small className="scout-company-muted">{inspection.detail}</small>}
        </div>
      )}
      <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border pt-3">
        {editingSourceId && (
          <Button type="button" size="sm" variant="outline" onClick={onCancelEdit}>
            Cancel edit
          </Button>
        )}
        <Button type="submit" size="sm" disabled={!canSave}>
          {saving ? "Saving…" : editingSourceId ? "Update source" : "Save source"}
        </Button>
      </div>
    </form>
  );
};
