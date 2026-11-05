import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type CompanyBrandingFormProps = {
  logoUrl: string;
  logoSourceUrl: string;
  saving: boolean;
  onLogoUrlChange: (value: string) => void;
  onLogoSourceUrlChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function CompanyBrandingForm({
  logoUrl,
  logoSourceUrl,
  saving,
  onLogoUrlChange,
  onLogoSourceUrlChange,
  onSubmit,
}: CompanyBrandingFormProps) {
  return (
    <form
      className="my-4 grid gap-3 rounded-xl border border-slate-700 bg-slate-900/80 p-4 text-white"
      onSubmit={onSubmit}
    >
      <div className="flex items-center gap-3">
        <h4>Company logo</h4>
        <span className="text-[10px] text-slate-400">Optional</span>
        {logoUrl && (
          <img
            src={logoUrl}
            alt="Company logo preview"
            className="h-9 w-9 rounded-md border border-slate-700 bg-white object-contain p-1"
          />
        )}
      </div>
      <label>
        Logo image URL
        <Input
          type="url"
          value={logoUrl}
          onChange={(event) => onLogoUrlChange(event.target.value)}
          placeholder="https://company.com/logo.png"
          className="mt-1 border-slate-700 bg-slate-950 text-white"
        />
      </label>
      <p className="text-[10px] text-slate-400">
        Scout currently accepts a logo URL and its evidence URL. A logo is not required to register
        or approve a company.
      </p>
      <label>
        Logo source / evidence URL
        <Input
          type="url"
          value={logoSourceUrl}
          onChange={(event) => onLogoSourceUrlChange(event.target.value)}
          placeholder="Official company page where the logo is shown"
          className="mt-1"
        />
      </label>
      <Button type="submit" variant="outline" className="w-fit" disabled={saving}>
        {saving ? "Saving…" : "Save logo details"}
      </Button>
    </form>
  );
}
