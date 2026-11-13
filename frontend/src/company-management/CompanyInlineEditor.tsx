import { useState, type FormEvent } from "react";
import { ImagePlus, Link2 } from "lucide-react";
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
            The employer's main public website. You can change this if the domain has moved.
          </span>
        </label>

        <div className="grid gap-2">
          <label className="flex items-center gap-2 text-sm font-medium text-foreground">
            <ImagePlus className="h-4 w-4 text-muted-foreground" />
            Company logo URL
          </label>
          <div className="flex min-w-0 flex-col gap-3 sm:flex-row">
            <div className="flex h-20 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted/40 p-2">
              {logoUrl.trim() && !logoFailed ? (
                <img
                  src={logoUrl.trim()}
                  alt="Company logo preview"
                  className="h-full w-full object-contain"
                  onError={() => setLogoFailed(true)}
                />
              ) : (
                <ImagePlus className="h-7 w-7 text-muted-foreground" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <Input
                type="url"
                value={logoUrl}
                onChange={(event) => {
                  setLogoUrl(event.target.value);
                  setLogoFailed(false);
                }}
                placeholder="https://example.com/assets/logo"
                aria-label="Company logo URL"
              />
              <p className="mt-1.5 flex items-start gap-1.5 text-xs font-normal text-muted-foreground">
                <Link2 className="mt-0.5 h-3 w-3 shrink-0" />
                Paste the direct public image address. Scout stores the URL, not the image file.
              </p>
              {logoUrl.trim() && logoFailed && (
                <p className="mt-1 text-xs text-destructive">
                  This address could not be previewed. Check that it points to a publicly accessible image.
                </p>
              )}
              {logoUrl.trim() && (
                <button
                  type="button"
                  className="mt-2 text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground"
                  onClick={() => {
                    setLogoUrl("");
                    setLogoFailed(false);
                  }}
                >
                  Clear logo URL
                </button>
              )}
            </div>
          </div>
        </div>
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
