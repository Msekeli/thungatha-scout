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
      <p className="mb-3 text-xs scout-company-muted">
        Add an employer from its official careers page. Scout will configure the source and import
        its vacancies.
      </p>
      <section className="scout-company-onboarding">
        <div className="mb-5">
          <h2 className="text-base font-semibold scout-company-heading">Employer details</h2>
          <p className="mt-1 text-sm scout-company-muted">
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
          <div className="scout-company-form-actions">
            <Button
              type="button"
              variant="outline"
              className="h-10 border-slate-600 bg-slate-900 px-5 text-slate-200 hover:bg-slate-800 hover:scout-company-heading"
              onClick={onCancel}
              disabled={busy}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="scout-company-add-button"
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
