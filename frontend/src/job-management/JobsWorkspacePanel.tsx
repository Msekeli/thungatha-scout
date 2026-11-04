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
};

export function JobsWorkspacePanel({ jobs, state }: Props) {
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/80 bg-card px-4 py-2.5 text-card-foreground shadow-lg shadow-black/20">
        <span className="text-[10px] font-medium text-muted-foreground">
          {jobs.loading ? "Refreshing data…" : "Updated from Scout records"}
        </span>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => void jobs.loadWorkspace()}
            disabled={jobs.loading || state.extracting}>
            <RefreshCw className={`mr-1 h-3.5 w-3.5 ${jobs.loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => void jobs.fetchJobs()}
            disabled={jobs.loading || state.extracting}>
            <BriefcaseBusiness className="mr-1 h-3.5 w-3.5" />
            {state.extracting ? "Fetching jobs…" : "Fetch jobs"}
          </Button>
        </div>
      </div>
      <DashboardOverview vacancyCount={jobs.vacancies.length}
        employerCount={jobs.employers.length} newVacancies24h={jobs.newVacancies24h}
        attentionCount={jobs.attentionCount} atsPerformance={jobs.atsPerformance} />
      <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyRecordsToolbar showArchived={state.showArchived}
            onShowArchivedChange={(show) => {
              state.setShowArchived(show);
              jobs.clearSelection();
            }}
            reviewFilter={state.reviewFilter} onReviewFilterChange={state.setReviewFilter}
            selectedEmployerId={state.selectedEmployerId}
            onEmployerChange={state.setSelectedEmployerId} employers={jobs.employers}
            onRefresh={() => void jobs.loadWorkspace()} loading={jobs.loading} />
          <VacancyRecordList vacancies={jobs.filteredVacancies} loading={jobs.loading}
            selectedVacancyId={jobs.selectedVacancyId} openingVacancyId={jobs.openingVacancyId}
            onOpenVacancy={(id) => void jobs.openVacancy(id, jobs.visibleVacancies)} />
        </section>
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyDetailsPanel vacancy={jobs.selectedVacancy}
            loading={Boolean(jobs.openingVacancyId)} reviewReason={jobs.reviewReason}
            saving={jobs.saving} onChangeReviewReason={jobs.setReviewReason}
            onClear={jobs.clearSelection} onDecision={(status) => void jobs.saveDecision(status)}
            onArchive={() => void jobs.archive()} onRestore={() => void jobs.restore()} />
        </section>
      </div>
    </section>
  );
}
