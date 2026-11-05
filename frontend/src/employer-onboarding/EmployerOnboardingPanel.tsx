import type { FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { OnboardingPreviewCard } from "./OnboardingDetectionStatus";
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
  atsKey: string;
  onChangeAtsKey: (value: string) => void;
  discovery: import("../api").CareersDiscovery | null;
  onDiscover: () => void;
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
  atsKey,
  onChangeAtsKey,
  discovery,
  onDiscover,
  inspecting,
  form,
  onChangeCompanyName,
  saving,
  onSubmit,
  onCancel,
}: EmployerOnboardingPanelProps) {
  return (
    <>
      <p className="mb-3 text-xs text-white/75">Add an employer using its official careers page.</p>
      <section className="w-full max-w-2xl rounded-xl border border-border bg-card p-4 shadow-sm sm:p-6">
        <form className="grid gap-4" onSubmit={onSubmit}>
          <OnboardingUrlForm
            companyName={form.name}
            onChangeCompanyName={onChangeCompanyName}
            sourceUrl={sourceUrl}
            onChangeSourceUrl={onChangeSourceUrl}
            atsKey={atsKey}
            onChangeAtsKey={onChangeAtsKey}
            onDetect={onDiscover}
            inspecting={inspecting}
          />
          <OnboardingDetectionStatus discovery={discovery} />
          <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border pt-3">
            <Button type="button" size="sm" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            {discovery && (
              <Button type="submit" size="sm" disabled={saving || inspecting}>
                {saving ? "Adding company…" : "Add Company"}
              </Button>
            )}
          </div>
        </form>
      </section>
    </>
  );
}
