import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { EmployerSource } from "../api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
export type SourceDecisionDraft = {
  status: string;
  permission_status: string;
  evidence_url: string;
  reason: string;
};

type SourceReviewPanelProps = {
  source: EmployerSource;
  decision?: SourceDecisionDraft;
  saving: boolean;
  onChange: (field: keyof SourceDecisionDraft, value: string) => void;
  onSave: () => void;
};

export function SourceReviewPanel(props: SourceReviewPanelProps) {
  return (
    <div className="grid gap-3 rounded-lg border border-border bg-muted/50 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <strong className="text-xs font-semibold text-foreground">Verification & permission</strong>
        <span className="text-[10px] text-muted-foreground">
          Company approval does not approve this source
        </span>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div className="grid gap-1 text-xs font-medium text-muted-foreground">
          <span>Source status</span>
          <Select
            value={decision?.status ?? source.status}
            onValueChange={(value) => onChange("status", value)}
          >
            <SelectTrigger aria-label="Source status" className="h-9 bg-card text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="discovered">Discovered</SelectItem>
              <SelectItem value="pending_verification">Pending verification</SelectItem>
              <SelectItem value="verified">Verified</SelectItem>
              <SelectItem value="temporarily_unavailable">Temporarily unavailable</SelectItem>
              <SelectItem value="invalid">Invalid</SelectItem>
              <SelectItem value="needs_review">Needs review</SelectItem>
              <SelectItem value="inactive">Inactive</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="grid gap-1 text-xs font-medium text-muted-foreground">
          <span>Permission</span>
          <Select
            value={decision?.permission_status ?? source.permission_status}
            onValueChange={(value) => onChange("permission_status", value)}
          >
            <SelectTrigger aria-label="Permission" className="h-9 bg-card text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="unknown">Unknown</SelectItem>
              <SelectItem value="allowed">Allowed</SelectItem>
              <SelectItem value="restricted">Restricted</SelectItem>
              <SelectItem value="needs_review">Needs review</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <label className="grid gap-1 text-xs font-medium text-muted-foreground">
        Evidence URL
        <Input
          type="url"
          className="bg-card"
          value={decision?.evidence_url ?? ""}
          onChange={(event) => onChange("evidence_url", event.target.value)}
          placeholder="Official employer page confirming this ATS relationship"
        />
      </label>
      <label className="grid gap-1 text-xs font-medium text-muted-foreground">
        Decision notes
        <Textarea
          className="bg-card"
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
