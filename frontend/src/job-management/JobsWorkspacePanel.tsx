import { DashboardOverview } from "../app-shell/DashboardOverview";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useJobsWorkspaceController } from "./useJobsWorkspaceController";
import { VacancyDetailsPanel } from "./VacancyDetailsPanel";
import { VacancyRecordList } from "./VacancyRecordList";
import { VacancyRecordsToolbar } from "./VacancyRecordsToolbar";

type Props = {
  jobs: ReturnType<typeof useJobsWorkspaceController>;
  state: ReturnType<typeof useScoutAppState>;
};

export function JobsWorkspacePanel({ jobs, state }: Props) {
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
      <div className="px-1 py-1">
        <DashboardOverview
          vacancyCount={jobs.dashboardMetrics.total_active}
          companyCount={jobs.employers.length}
          newCount={jobs.dashboardMetrics.new_last_24_hours}
          freshCount={jobs.dashboardMetrics.fresh_vacancies}
          recentCount={jobs.dashboardMetrics.recent_vacancies}
          agingCount={jobs.dashboardMetrics.aging_vacancies}
          staleCount={jobs.dashboardMetrics.stale_vacancies}
          undatedCount={jobs.dashboardMetrics.undated_vacancies}
          runSummary={jobs.runSummary ?? jobs.latestRunSummary}
          extracting={state.extracting}
        />
      </div>
      <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyRecordsToolbar
            selectedEmployerId={state.selectedEmployerId}
            onEmployerChange={state.setSelectedEmployerId}
            employers={jobs.employers}
            locationScope={state.locationScope}
            ageFilter={state.vacancyAgeFilter}
            onAgeFilterChange={state.setVacancyAgeFilter}
            onLocationChange={state.setLocationScope}
            totalVacancies={jobs.totalVacancies}
            loadedVacancies={jobs.vacancies.length}
          />
          <VacancyRecordList
            vacancies={jobs.filteredVacancies}
            loading={jobs.loading || jobs.loadingFirstPage}
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
