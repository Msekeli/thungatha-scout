import type { FC, FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { GreenhouseInspection } from "../api";

type SourceRegistrationFormProps = {
  editingSourceId: string | null;
  sourceUrl: string;
  onChangeSourceUrl: (value: string) => void;
  onInspect: () => void;
  inspection: GreenhouseInspection | null;
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
    <form
      className="mt-5 grid gap-3 rounded-lg border border-border bg-muted/50 p-4"
      onSubmit={onSaveSource}
    >
      <h4 className="text-sm font-semibold text-foreground">
        {editingSourceId ? "Update Greenhouse source" : "Register Greenhouse source"}
      </h4>
      <label className="grid gap-1 text-xs font-medium text-muted-foreground">
        Official careers / job board URL
        <Input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="https://job-boards.greenhouse.io/company"
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
        {inspecting ? "Checking source…" : "Check Greenhouse source"}
      </Button>
      {inspection && (
        <div className="grid gap-1 rounded-lg border border-border bg-card p-3 text-xs">
          <strong className="text-foreground">{inspection.board_name || inspection.board_token}</strong>
          <span className="text-muted-foreground">
            {inspection.outcome} · {inspection.jobs.length} sample jobs
          </span>
          {inspection.detail && <small className="text-muted-foreground">{inspection.detail}</small>}
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
