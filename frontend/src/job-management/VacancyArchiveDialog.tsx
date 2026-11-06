import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Vacancy } from "../api";

const reasons = [
  "Job filled", "Job closed or expired", "Employer removed the listing",
  "Duplicate vacancy", "Outside Scout's coverage or eligibility",
  "Other administrative reason",
] as const;

type Props = {
  vacancy: Vacancy | null;
  open: boolean;
  saving: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (reason: string) => Promise<boolean>;
};

export function VacancyArchiveDialog({ vacancy, open, saving, onOpenChange, onConfirm }: Props) {
  const [reason, setReason] = useState("");
  useEffect(() => { if (open) setReason(""); }, [open, vacancy?.id]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Archive vacancy</DialogTitle>
          <DialogDescription>
            Select why you are archiving {vacancy?.title ?? "this vacancy"}.
            This reason will be saved with the vacancy.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="vacancy-archive-reason">Archive reason</label>
          <Select value={reason} onValueChange={setReason} disabled={saving}>
            <SelectTrigger id="vacancy-archive-reason">
              <SelectValue placeholder="Select a reason" />
            </SelectTrigger>
            <SelectContent>
              {reasons.map((option) => <SelectItem key={option} value={option}>{option}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" disabled={saving} onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button disabled={!reason || saving} onClick={async () => {
            if (await onConfirm(reason)) onOpenChange(false);
          }}>
            {saving ? "Archiving…" : "Archive vacancy"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
