import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Employer } from "../api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CompanyOrganizationTypeSelect } from "./CompanyOrganizationTypeSelect";

type Values = {
  name: string;
  legal_name: string | null;
  website_url: string | null;
  organization_type: string;
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
  const [fields, setFields] = useState({
    name: "",
    legal_name: "",
    website_url: "",
    organization_type: "unresolved",
    city: "",
    province: "",
    country: "",
  });
  useEffect(() => {
    setFields({
      name: employer?.name ?? "",
      legal_name: employer?.legal_name ?? "",
      website_url: employer?.website_url ?? "",
      organization_type: employer?.organization_type ?? "unresolved",
      city: employer?.city ?? "",
      province: employer?.province ?? "",
      country: employer?.country ?? "",
    });
  }, [employer, open]);
  const change = (key: keyof typeof fields, value: string) =>
    setFields((current) => ({ ...current, [key]: value }));
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSave({
      name: fields.name.trim(),
      legal_name: fields.legal_name.trim() || null,
      website_url: fields.website_url.trim() || null,
      organization_type: fields.organization_type,
      city: fields.city.trim() || null,
      province: fields.province.trim() || null,
      country: fields.country.trim() || null,
    });
  };
  const textField = (label: string, key: keyof typeof fields, placeholder = "") => (
    <label className="grid gap-1.5 text-sm font-medium">
      {label}
      <Input
        value={fields[key]}
        placeholder={placeholder}
        onChange={(event) => change(key, event.target.value)}
      />
    </label>
  );
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit company</DialogTitle>
          <DialogDescription>Update the company profile and its official links.</DialogDescription>
        </DialogHeader>
        <form onSubmit={submit} className="grid gap-4">
          {textField("Company name", "name")}
          {textField("Legal name", "legal_name")}
          {textField("Official website", "website_url", "https://company.com")}
          <CompanyOrganizationTypeSelect
            value={fields.organization_type}
            onChange={(value) => change("organization_type", value)}
          />
          <div className="grid gap-3 sm:grid-cols-3">
            {textField("City", "city")}
            {textField("Province", "province")}
            {textField("Country", "country")}
          </div>
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
