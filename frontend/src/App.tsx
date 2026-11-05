import type { FormEvent } from "react";
import { AppShellHeader } from "./app-shell/AppShellHeader";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { JobsWorkspacePanel } from "./job-management/JobsWorkspacePanel";
import { CompaniesWorkspacePanel } from "./company-management/CompaniesWorkspacePanel";
import { EmployerOnboardingPanel } from "./employer-onboarding/EmployerOnboardingPanel";
import { useScoutApplicationController } from "./useScoutApplicationController";

export default function App() {
  const { state, jobs, companies, onboarding } = useScoutApplicationController();
  const saveBranding = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await companies.saveBranding();
  };

  return (
    <main className="mx-auto flex h-screen max-w-[1600px] flex-col overflow-hidden bg-[#050a14] px-4 pb-3 pt-4 text-white md:px-8">
      <AppShellHeader
        activePage={state.page}
        onSelectPage={state.setPage}
        onRefresh={() => void jobs.loadWorkspace()}
        refreshing={jobs.loading}
      />
      <OperationalAlerts
        error={state.error}
        notice={state.notice}
        canUndo={jobs.canUndoDecision}
        onUndo={() => void jobs.undoLastDecision()}
        onDismissError={state.dismissError}
        onDismissNotice={state.dismissNotice}
      />
      {state.page === "jobs" && <JobsWorkspacePanel jobs={jobs} state={state} />}
      {state.page === "companies" && (
        <CompaniesWorkspacePanel
          state={state}
          jobs={jobs}
          companies={companies}
          onboarding={onboarding}
          onSaveBranding={saveBranding}
        />
      )}
      {state.page === "add-company" && (
        <EmployerOnboardingPanel
          sourceUrl={state.sourceUrl}
          onChangeSourceUrl={(value) => {
            state.setSourceUrl(value);
            onboarding.setDiscovery(null);
          }}
          atsKey={onboarding.atsKey}
          onChangeAtsKey={(value) => {
            onboarding.setAtsKey(value);
            onboarding.setDiscovery(null);
          }}
          discovery={onboarding.discovery}
          onDiscover={onboarding.discover}
          inspecting={onboarding.inspecting}
          form={state.form}
          onChangeCompanyName={(value) => state.setForm((current) => ({ ...current, name: value }))}
          saving={state.saving}
          onSubmit={onboarding.submit}
          onCancel={() => {
            state.setPage("companies");
            onboarding.setDiscovery(null);
          }}
        />
      )}
      <footer className="mt-5 border-t border-white/15 pt-3 text-[10px] text-white/65">
        Scout is a private operations workspace. Only verified, quality-checked records are eligible
        for publishing to Thungatha.
      </footer>
    </main>
  );
}
