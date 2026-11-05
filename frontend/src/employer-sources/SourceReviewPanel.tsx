import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { EmployerSource } from "../api";
import { SourceReviewSelect } from "./SourceReviewSelect";

export type SourceDecisionDraft = {
  status: string;
  permission_status: string;
  evidence_url: string;
  reason: string;
};

type Props = {
  source: EmployerSource;
  decision?: SourceDecisionDraft;
  saving: boolean;
  onChange: (field: keyof SourceDecisionDraft, value: string) => void;
  onSave: () => void;
};

const statusOptions = [
  "discovered",
  "pending_verification",
  "verified",
  "temporarily_unavailable",
  "invalid",
  "needs_review",
  "inactive",
].map((value) => ({ value, label: value.replaceAll("_", " ") }));
const permissionOptions = ["unknown", "allowed", "restricted", "needs_review"].map((value) => ({
  value,
  label: value.replaceAll("_", " "),
}));

export function SourceReviewPanel({ source, decision, saving, onChange, onSave }: Props) {
  return (
    <div className="scout-company-form-section">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <strong className="text-xs font-semibold scout-company-heading">
          Verification & permission
        </strong>
        <span className="text-[10px] scout-company-muted">
          Company approval does not approve this source
        </span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <SourceReviewSelect
          label="Source status"
          value={decision?.status ?? source.status}
          onChange={(value) => onChange("status", value)}
          options={statusOptions}
        />
        <SourceReviewSelect
          label="Permission"
          value={decision?.permission_status ?? source.permission_status}
          onChange={(value) => onChange("permission_status", value)}
          options={permissionOptions}
        />
      </div>
      <label className="grid gap-1 text-xs font-medium scout-company-muted">
        Evidence URL
        <Input
          type="url"
          className="scout-company-field"
          value={decision?.evidence_url ?? ""}
          onChange={(event) => onChange("evidence_url", event.target.value)}
          placeholder="Official employer page confirming this ATS relationship"
        />
      </label>
      <label className="grid gap-1 text-xs font-medium scout-company-muted">
        Decision notes
        <Textarea
          className="scout-company-field"
          value={decision?.reason ?? ""}
          onChange={(event) => onChange("reason", event.target.value)}
          placeholder="Why this source status and permission were chosen"
        />
      </label>
      <Button type="button" size="sm" className="w-fit" disabled={saving} onClick={onSave}>
        {saving ? "Saving…" : "Save source decision"}
      </Button>
    </div>
  );
}
