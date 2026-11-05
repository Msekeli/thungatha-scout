import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { OnboardingUrlForm } from "./OnboardingUrlForm";

type EmployerRegistrationDraft = {
  name: string;
  website_url: string;
  organization_type: string;
  city: string;
  province: string;
  country: string;
};

type EmployerOnboardingPanelProps = {
  sourceUrl: string;
  onChangeSourceUrl: (value: string) => void;
  inspecting: boolean;
  form: EmployerRegistrationDraft;
  onChangeCompanyName: (value: string) => void;
  saving: boolean;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
};

export function EmployerOnboardingPanel({
  sourceUrl,
  onChangeSourceUrl,
  inspecting,
  form,
  onChangeCompanyName,
  saving,
  onSubmit,
  onCancel,
}: EmployerOnboardingPanelProps) {
  const busy = inspecting || saving;
  return (
    <>
      <p className="mb-3 text-xs text-slate-300">
        Add an employer from its official careers page. Scout will configure the source and import
        its vacancies.
      </p>
      <section className="w-full max-w-2xl rounded-xl border border border-slate-700 bg-slate-900 p-5 text-white shadow-xl shadow-black/30 sm:p-7">
        <div className="mb-5">
          <h2 className="text-base font-semibold text-white">Employer details</h2>
          <p className="mt-1 text-sm text-slate-400">
            Enter the careers page and confirm the company name before adding it.
          </p>
        </div>
        <form className="grid gap-6" onSubmit={onSubmit}>
          <OnboardingUrlForm
            companyName={form.name}
            onChangeCompanyName={onChangeCompanyName}
            sourceUrl={sourceUrl}
            onChangeSourceUrl={onChangeSourceUrl}
          />
          <div className="flex flex-col-reverse gap-3 border-t border-slate-700 pt-5 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="outline"
              className="h-10 border-slate-300 bg-slate-950 px-5 text-slate-200 hover:bg-slate-100 hover:text-white"
              onClick={onCancel}
              disabled={busy}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="h-10 bg-cyan-500 text-slate-950 px-6 text-white shadow-sm hover:bg-cyan-400"
              disabled={busy || !sourceUrl.trim()}
            >
              {inspecting ? "Checking careers page…" : saving ? "Adding company…" : "Add Company"}
            </Button>
          </div>
        </form>
      </section>
    </>
  );
}
