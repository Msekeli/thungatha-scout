import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Employer } from "../api";

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
  }) => void;
  onCancel: () => void;
};

export function CompanyInlineEditor({ employer, saving, onSave, onCancel }: Props) {
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
    });
  };

  return (
    <form className="scout-company-inline-editor" onSubmit={submit}>
      <label className="scout-company-form-label">
        Company name
        <Input name="name" defaultValue={employer.name} required />
      </label>
      <label className="scout-company-form-label">
        Official website
        <Input
          name="website_url"
          type="url"
          defaultValue={employer.website_url ?? ""}
          placeholder="https://company.com"
        />
      </label>
      <div className="flex justify-end gap-2">
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
