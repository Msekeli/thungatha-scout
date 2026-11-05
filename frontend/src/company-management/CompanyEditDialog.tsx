import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Employer } from "../api";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CompanyEditFields, type CompanyEditFieldValues } from "./CompanyEditFields";

type Values = Omit<
  CompanyEditFieldValues,
  "legal_name" | "website_url" | "city" | "province" | "country"
> & {
  legal_name: string | null;
  website_url: string | null;
  city: string | null;
  province: string | null;
  country: string | null;
};
type Props = {
  employer: Employer | null;
  open: boolean;
  saving: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (values: Values) => void;
};

export function CompanyEditDialog({ employer, open, saving, onOpenChange, onSave }: Props) {
  const [fields, setFields] = useState<CompanyEditFieldValues>({
    name: "",
    legal_name: "",
    website_url: "",
    organization_type: "unresolved",
    city: "",
    province: "",
    country: "",
  });
  useEffect(
    () =>
      setFields({
        name: employer?.name ?? "",
        legal_name: employer?.legal_name ?? "",
        website_url: employer?.website_url ?? "",
        organization_type: employer?.organization_type ?? "unresolved",
        city: employer?.city ?? "",
        province: employer?.province ?? "",
        country: employer?.country ?? "",
      }),
    [employer, open],
  );
  const change = (key: keyof CompanyEditFieldValues, value: string) =>
    setFields((current) => ({ ...current, [key]: value }));
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSave({
      ...fields,
      name: fields.name.trim(),
      legal_name: fields.legal_name.trim() || null,
      website_url: fields.website_url.trim() || null,
      city: fields.city.trim() || null,
      province: fields.province.trim() || null,
      country: fields.country.trim() || null,
    });
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="scout-company-dialog scout-company-edit-dialog">
        <DialogHeader>
          <DialogTitle className="scout-company-heading">Edit company</DialogTitle>
          <DialogDescription className="scout-company-dialog-copy">
            Update the company profile and its official links.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="scout-company-edit-fields">
          <CompanyEditFields fields={fields} onChange={change} />
          <div className="flex justify-end gap-2 border-t border-border pt-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving || !fields.name.trim()}>
              {saving ? "Saving…" : "Save changes"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
