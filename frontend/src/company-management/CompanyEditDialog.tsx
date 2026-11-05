import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Employer } from "../api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

type Props = {
  employer: Employer | null;
  open: boolean;
  saving: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (values: { name: string; website_url: string | null; organization_type: string }) => void;
};

export function CompanyEditDialog({ employer, open, saving, onOpenChange, onSave }: Props) {
  const [name, setName] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [organizationType, setOrganizationType] = useState("unresolved");

  useEffect(() => {
    setName(employer?.name ?? "");
    setWebsiteUrl(employer?.website_url ?? "");
    setOrganizationType(employer?.organization_type ?? "unresolved");
  }, [employer, open]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSave({
      name: name.trim(),
      website_url: websiteUrl.trim() || null,
      organization_type: organizationType,
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit company</DialogTitle>
          <DialogDescription>
            Update the employer identity. Recruitment sources remain linked to this company.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="grid gap-4">
          <label className="grid gap-1.5 text-sm font-medium">
            Company name
            <Input required value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="grid gap-1.5 text-sm font-medium">
            Official website
            <Input
              type="url"
              value={websiteUrl}
              onChange={(event) => setWebsiteUrl(event.target.value)}
              placeholder="https://company.com"
            />
          </label>
          <label className="grid gap-1.5 text-sm font-medium">
            Organisation type
            <Select value={organizationType} onValueChange={setOrganizationType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="direct_employer">Direct employer</SelectItem>
                <SelectItem value="recruitment_agency">Recruitment agency</SelectItem>
                <SelectItem value="staffing_company">Staffing company</SelectItem>
                <SelectItem value="hybrid">Hybrid</SelectItem>
                <SelectItem value="other">Other</SelectItem>
                <SelectItem value="unresolved">Unresolved</SelectItem>
              </SelectContent>
            </Select>
          </label>
          <div className="flex justify-end gap-2 border-t border-border pt-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving || !name.trim()}>
              {saving ? "Saving…" : "Save changes"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
