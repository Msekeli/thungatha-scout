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
    <section className="flex min-h-0 min-w-0 flex-col gap-4 overflow-y-auto scout-company-profile">
      {editing ? (
        <CompanyInlineEditor
          key={employer.id}
          employer={employer}
          saving={state.saving}
          onCancel={() => setEditing(false)}
          onSave={async (values) => {
            if (await companies.updateDetails(values)) setEditing(false);
          }}
        />
      ) : (
        <CompanyProfileHeader employer={employer} jobsCount={jobsCount} />
      )}
      <CompanyProfileActions
        companyName={employer.name}
        saving={state.saving}
        editing={editing}
        onEdit={() => setEditing((current) => !current)}
        onDelete={() => void companies.deleteCompany()}
      />
      <CompanySourcesPanel
        state={state}
        companies={companies}
        onboarding={onboarding}
      />
    </section>
  );
}
