import { useState } from "react";
import { CompanyProfileActions } from "./CompanyProfileActions";
import { CompanyProfileHeader } from "./CompanyProfileHeader";
import { CompanyInlineEditor } from "./CompanyInlineEditor";
import { CompanySourcesPanel } from "./CompanySourcesPanel";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "../job-management/useJobsWorkspaceController";
import type { useCompaniesWorkspaceController } from "./useCompaniesWorkspaceController";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";

type Props = {
  state: ReturnType<typeof useScoutAppState>;
  jobs: ReturnType<typeof useJobsWorkspaceController>;
  companies: ReturnType<typeof useCompaniesWorkspaceController>;
  onboarding: ReturnType<typeof useEmployerOnboardingController>;
};

export function CompanyProfilePanel({ state, jobs, companies, onboarding }: Props) {
  const employer = companies.employer;
  const [editing, setEditing] = useState(false);
  if (!employer) return null;
  const jobsCount = jobs.vacancies.filter((item) => item.employer_id === employer.id).length;

  return (
    <section className="scout-company-profile flex min-h-0 min-w-0 flex-col gap-5 overflow-y-auto pr-1">
      <CompanyProfileHeader key={employer.id} employer={employer} jobsCount={jobsCount} />
      {editing && (
        <CompanyInlineEditor
          key={employer.id}
          employer={employer}
          saving={state.saving}
          onCancel={() => setEditing(false)}
          onSave={async (values) => {
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
            const brandingSaved = await companies.saveBranding(values.logo_url);
            if (brandingSaved) setEditing(false);
          }}
        />
      )}
      <CompanySourcesPanel state={state} companies={companies} onboarding={onboarding} />
      <footer className="scout-company-footer">
        <span className="text-xs text-muted-foreground">Company actions</span>
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
