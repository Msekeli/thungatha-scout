import { BriefcaseBusiness, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DashboardOverview } from "../app-shell/DashboardOverview";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "./useJobsWorkspaceController";
import { VacancyDetailsPanel } from "./VacancyDetailsPanel";
import { VacancyRecordList } from "./VacancyRecordList";
import { VacancyRecordsToolbar } from "./VacancyRecordsToolbar";

type Props = {
  jobs: ReturnType<typeof useJobsWorkspaceController>;
  state: ReturnType<typeof useScoutAppState>;
  vacancyChange: number;
};

export function JobsWorkspacePanel({ jobs, state, vacancyChange }: Props) {
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
      <div className="flex flex-wrap items-center justify-between gap-4 px-1 py-1">
        <DashboardOverview
          vacancyCount={jobs.dashboardMetrics.total_active}
          vacancyChange={vacancyChange}
        />
        <div className="flex shrink-0 gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-9 border-input bg-background text-primary hover:bg-accent hover:text-accent-foreground"
            onClick={() => void jobs.loadWorkspace()}
            disabled={jobs.loading || state.extracting}
          >
            <RefreshCw className={"mr-1 h-3.5 w-3.5 " + (jobs.loading ? "animate-spin" : "")} />
            Refresh
          </Button>
          <Button
            size="sm"
            className="h-9 bg-scout-cyan text-scout-navy hover:brightness-95"
            onClick={() => void jobs.fetchJobs()}
            disabled={jobs.loading || state.extracting}
          >
            <BriefcaseBusiness className="mr-1 h-3.5 w-3.5" />
            {state.extracting ? "Fetching jobs…" : "Fetch jobs"}
          </Button>
        </div>
      </div>
      <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyRecordsToolbar
            selectedEmployerId={state.selectedEmployerId}
            onEmployerChange={state.setSelectedEmployerId}
            employers={jobs.employers}
            locationScope={state.locationScope}
            onLocationChange={state.setLocationScope}
            totalVacancies={jobs.totalVacancies}
            loadedVacancies={jobs.vacancies.length}
          />
          <VacancyRecordList
            vacancies={jobs.filteredVacancies}
            loading={jobs.loading}
            loadingMore={jobs.loadingMore}
            hasMore={jobs.hasMoreVacancies}
            onLoadMore={jobs.loadMoreVacancies}
            selectedVacancyId={jobs.selectedVacancyId}
            openingVacancyId={jobs.openingVacancyId}
            savingVacancyId={jobs.savingVacancyId}
            onOpenVacancy={(id) => void jobs.openVacancy(id, jobs.visibleVacancies)}
            onArchive={(vacancy, reason) => jobs.archive(vacancy, reason)}
            onRestore={(vacancy) => void jobs.restore(vacancy)}
          />
        </section>
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyDetailsPanel
            vacancy={jobs.selectedVacancy}
            loading={Boolean(jobs.openingVacancyId)}
          />
        </section>
      </div>
    </section>
  );
}
