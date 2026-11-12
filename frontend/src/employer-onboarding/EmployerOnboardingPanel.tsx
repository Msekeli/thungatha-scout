import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { OnboardingUrlForm } from "./OnboardingUrlForm";
import type { EmployerDuplicateMatch } from "./findEmployerDuplicate";

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
  duplicate: EmployerDuplicateMatch | null;
  onOpenExisting: (employerId: string) => void;
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
  duplicate,
  onOpenExisting,
}: EmployerOnboardingPanelProps) {
  const busy = inspecting || saving;
  return (
    <>
      <p className="mb-3 text-xs scout-company-muted">
        Add an employer using its official Greenhouse, Lever, Teamtailor or Workable board URL.
        Vacancy extraction starts after registration in the background.
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
          {duplicate?.kind === "source" ? (
            <div
              role="alert"
              className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm"
            >
              <p className="font-semibold">This recruitment source has already been added.</p>
              <p className="mt-1">
                {duplicate.employer.name} already has this careers URL registered.
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={() => onOpenExisting(duplicate.employer.id)}
              >
                Open existing company
              </Button>
            </div>
          ) : duplicate?.kind === "employer" ? (
            <div className="rounded-lg border border-blue-500/40 bg-blue-500/10 p-3 text-sm">
              <p className="font-semibold">This company is already in Scout.</p>
              <p className="mt-1">
                This URL will be added as another recruitment source under {duplicate.employer.name}
                . Scout will not create a second company.
              </p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-3"
                onClick={() => onOpenExisting(duplicate.employer.id)}
              >
                Open existing company
              </Button>
            </div>
          ) : null}
          <div className="scout-company-form-actions">
            <Button
              type="button"
              variant="outline"
              className="scout-company-cancel-button"
              onClick={onCancel}
              disabled={busy}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="scout-company-add-button"
              disabled={busy || !sourceUrl.trim() || duplicate?.kind === "source"}
            >
              {inspecting
                ? "Checking careers page…"
                : saving
                  ? "Adding company…"
                  : duplicate?.kind === "employer"
                    ? "Add source to existing company"
                    : "Add Company"}
            </Button>
          </div>
        </form>
      </section>
    </>
  );
}
