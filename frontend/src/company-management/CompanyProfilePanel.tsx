import { useState } from "react";
import { CompanyProfileActions } from "./CompanyProfileActions";
import { CompanyProfileHeader } from "./CompanyProfileHeader";
import { CompanyInlineEditor } from "./CompanyInlineEditor";
import { CompanySourcesPanel } from "./CompanySourcesPanel";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useCompaniesWorkspaceController } from "./useCompaniesWorkspaceController";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";

type Props = {
  state: ReturnType<typeof useScoutAppState>;
  companies: ReturnType<typeof useCompaniesWorkspaceController>;
  onboarding: ReturnType<typeof useEmployerOnboardingController>;
};

export function CompanyProfilePanel({ state, companies, onboarding }: Props) {
  const employer = companies.employer;
  const [editing, setEditing] = useState(false);
  if (!employer) return null;
  const jobsCount = employer.vacancy_count ?? 0;

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col gap-5 overflow-y-auto px-6 py-5 pr-5">
      <CompanyProfileHeader key={employer.id} employer={employer} jobsCount={jobsCount} />
      {editing && (
        <CompanyInlineEditor
          key={employer.id}
          employer={employer}
          saving={state.saving}
          onCancel={() => setEditing(false)}
          onSave={async (values) => {
            const detailsChanged =
              values.name !== employer.name ||
              values.website_url !== (employer.website_url ?? null);
            const logoChanged = values.logo_url !== (employer.logo_url ?? "");
            if (detailsChanged) {
              const detailsSaved = await companies.updateDetails({
                name: values.name,
                legal_name: values.legal_name,
                website_url: values.website_url,
                organization_type: values.organization_type,
                city: values.city,
                province: values.province,
                country: values.country,
              });
              if (!detailsSaved) return;
            }
            if (logoChanged) {
              const brandingSaved = await companies.saveBranding(values.logo_url);
              if (!brandingSaved) return;
            }
            setEditing(false);
          }}
        />
      )}
      <CompanySourcesPanel state={state} companies={companies} onboarding={onboarding} />
      <footer className="flex flex-col gap-3 border-t border-border pt-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Company actions
        </span>
        <CompanyProfileActions
          companyName={employer.name}
          saving={state.saving}
          editing={editing}
          onEdit={() => setEditing((current) => !current)}
          onDelete={() => void companies.deleteCompany()}
        />
      </footer>
    </section>
  );
}
