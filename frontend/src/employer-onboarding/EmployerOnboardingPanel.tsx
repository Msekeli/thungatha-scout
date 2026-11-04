import type { FormEvent } from "react";
import type { CareersDiscovery } from "../api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { OnboardingPreviewCard } from "./OnboardingPreviewCard";
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
  discovery: CareersDiscovery | null;
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
      <p className="mb-3 text-xs text-muted-foreground">
        Register a company and connect its official careers source.
      </p>
      <section className="w-full max-w-2xl rounded-xl border border-border bg-card p-4 shadow-sm sm:p-6">
        <form className="grid gap-4" onSubmit={onSubmit}>
          <OnboardingUrlForm
            sourceUrl={sourceUrl}
            onChangeSourceUrl={onChangeSourceUrl}
            atsKey={atsKey}
            onChangeAtsKey={onChangeAtsKey}
            onDetect={onDiscover}
            inspecting={inspecting}
          />
          <OnboardingPreviewCard discovery={discovery} />
          {discovery && (
            <label>
              Company name
              <Input
                value={form.name}
                onChange={(event) => onChangeCompanyName(event.target.value)}
                placeholder="Detected company name"
                required
              />
            </label>
          )}
          <div className="flex flex-wrap items-center justify-end gap-2 border-t border-border pt-3">
            <Button type="button" size="sm" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            {discovery && (
              <Button
                type="submit"
                size="sm"
                disabled={
                  saving ||
                  !discovery.complete ||
                  !["success", "empty"].includes(discovery.outcome)
                }
              >
                {saving ? "Registering and retrieving…" : "Confirm & register"}
              </Button>
            )}
          </div>
        </form>
      </section>
    </>
  );
}
