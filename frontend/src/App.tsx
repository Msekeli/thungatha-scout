import { AppShellHeader } from "./app-shell/AppShellHeader";
import { OperationalAlerts } from "./app-shell/OperationalAlerts";
import { JobsWorkspacePanel } from "./job-management/JobsWorkspacePanel";
import { IngestionOperationsPanel } from "./app-shell/IngestionOperationsPanel";
import { CompaniesWorkspacePanel } from "./company-management/CompaniesWorkspacePanel";
import { AddCompanyDialog } from "./company-management/AddCompanyDialog";
import { useScoutApplicationController } from "./useScoutApplicationController";
import { useCompanyJobChanges } from "./company-management/useCompanyJobChanges";
export default function App() {
  const { state, jobs, companies, onboarding } = useScoutApplicationController();
  const companyJobChanges = useCompanyJobChanges(state.page, jobs.employers, jobs.vacancies);
  const addingCompany = state.page === "add-company";
  return (
    <main className="mx-auto flex h-screen max-w-[1600px] flex-col overflow-hidden scout-app-shell px-4 pb-3 pt-4 md:px-8">
      <AppShellHeader
        activePage={addingCompany ? "companies" : state.page}
        onSelectPage={state.setPage}
        onRefresh={() => void jobs.loadWorkspace()}
        refreshing={jobs.loading}
      />
      <OperationalAlerts
        error={state.error}
        notice={state.notice}
        onDismissError={state.dismissError}
        onDismissNotice={state.dismissNotice}
      />
      {state.page === "operations" && (
        <IngestionOperationsPanel
          employers={jobs.employers}
          sources={jobs.dashboardSources}
          runs={jobs.extractionRuns}
          running={state.extracting}
          refreshing={jobs.loading}
          onRunNow={() => void jobs.fetchJobs()}
          onRefresh={() => void jobs.loadWorkspace()}
        />
      )}
      {state.page === "jobs" && (
        <JobsWorkspacePanel jobs={jobs} state={state} />
      )}
      {(state.page === "companies" || addingCompany) && (
        <CompaniesWorkspacePanel
          state={state}
          jobs={jobs}
          companies={companies}
          onboarding={onboarding}
          currentJobsByEmployer={companyJobChanges.currentJobsByEmployer}
          jobChangesByEmployer={companyJobChanges.jobChangesByEmployer}
        />
      )}
      <AddCompanyDialog state={state} onboarding={onboarding} />
      <footer className="scout-app-footer">
        Scout is a private operations workspace. Only verified, quality-checked records are eligible
        for publishing to Thungatha.
      </footer>
    </main>
  );
}
