import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Employer } from "../api";
import { CompanyLogoUrlField } from "./CompanyLogoUrlField";

type Props = {
  employer: Employer;
  saving: boolean;
  onSave: (values: {
    name: string;
    legal_name: string | null;
    website_url: string | null;
    organization_type: string;
    city: string | null;
    province: string | null;
    country: string | null;
    logo_url: string;
  }) => void;
  onCancel: () => void;
};

export function CompanyInlineEditor({ employer, saving, onSave, onCancel }: Props) {
  const [logoUrl, setLogoUrl] = useState(employer.logo_url ?? "");
  const [logoFailed, setLogoFailed] = useState(false);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    onSave({
      name: String(data.get("name") ?? "").trim(),
      website_url: String(data.get("website_url") ?? "").trim() || null,
      legal_name: employer.legal_name ?? null,
      organization_type: employer.organization_type,
      city: employer.city ?? null,
      province: employer.province ?? null,
      country: employer.country ?? null,
      logo_url: logoUrl.trim(),
    });
  };

  return (
    <form className="rounded-xl border border-border bg-card p-4 sm:p-5" onSubmit={submit}>
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-foreground">Edit company profile</h4>
        <p className="mt-1 text-xs text-muted-foreground">
          Update the company name, official website and logo address.
        </p>
      </div>
      <div className="grid gap-4">
        <label className="grid gap-1.5 text-sm font-medium text-foreground">
          Company name
          <Input name="name" defaultValue={employer.name} required />
        </label>
        <label className="grid gap-1.5 text-sm font-medium text-foreground">
          Official website
          <Input
            name="website_url"
            type="url"
            defaultValue={employer.website_url ?? ""}
            placeholder="https://company.com"
          />
          <span className="text-xs font-normal text-muted-foreground">
            The employer's main public website. Change this if the domain has moved.
          </span>
        </label>
        <CompanyLogoUrlField
          value={logoUrl}
          failed={logoFailed}
          onChange={(value) => {
            setLogoUrl(value);
            setLogoFailed(false);
          }}
          onPreviewError={() => setLogoFailed(true)}
        />
      </div>
      <div className="mt-5 flex justify-end gap-2 border-t border-border pt-4">
        <Button type="button" variant="outline" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save changes"}
        </Button>
      </div>
    </form>
  );
}
