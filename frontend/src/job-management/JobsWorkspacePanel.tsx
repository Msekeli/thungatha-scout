import { BriefcaseBusiness, RefreshCw } from "lucide-react";
import type { Employer, Vacancy } from "../api";
import { Button } from "@/components/ui/button";
import { DashboardOverview } from "../app-shell/DashboardOverview";
import { VacancyDetailsPanel } from "./VacancyDetailsPanel";
import { VacancyRecordList } from "./VacancyRecordList";
import { VacancyRecordsToolbar } from "./VacancyRecordsToolbar";
import type { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";

type JobsWorkspacePanelProps = {
  loading: boolean;
  extracting: boolean;
  onRefresh: () => void;
  onFetchJobs: () => void;
  vacancies: Vacancy[];
  employers: Employer[];
  newVacancies24h: number;
  attentionCount: number;
  atsPerformance: ReturnType<typeof useScoutDashboardMetrics>["atsPerformance"];
  showArchived: boolean;
  onShowArchivedChange: (showArchived: boolean) => void;
  reviewFilter: string;
  onReviewFilterChange: (value: string) => void;
  selectedEmployerId: string;
  onEmployerChange: (value: string) => void;
  filteredVacancies: Vacancy[];
  visibleVacancies: Vacancy[];
  selectedVacancyId: string | null;
  openingVacancyId: string | null;
  onOpenVacancy: (vacancyId: string, visibleVacancies: Vacancy[]) => void;
  selectedVacancy: Vacancy | null;
  reviewReason: string;
  vacancySaving: boolean;
  onChangeReviewReason: (value: string) => void;
  onClearSelection: () => void;
  onDecision: (status: Vacancy["review_status"]) => void;
  onArchive: () => void;
  onRestore: () => void;
};

export function JobsWorkspacePanel({
  loading,
  extracting,
  onRefresh,
  onFetchJobs,
  vacancies,
  employers,
  newVacancies24h,
  attentionCount,
  atsPerformance,
  showArchived,
  onShowArchivedChange,
  reviewFilter,
  onReviewFilterChange,
  selectedEmployerId,
  onEmployerChange,
  filteredVacancies,
  visibleVacancies,
  selectedVacancyId,
  openingVacancyId,
  onOpenVacancy,
  selectedVacancy,
  reviewReason,
  vacancySaving,
  onChangeReviewReason,
  onClearSelection,
  onDecision,
  onArchive,
  onRestore,
}: JobsWorkspacePanelProps) {
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-3 pt-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-[10px] font-medium text-muted-foreground/70">
          {loading ? "Refreshing data…" : "Updated from Scout records"}
        </span>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-8 bg-card"
            onClick={onRefresh}
            disabled={loading || extracting}
          >
            <RefreshCw className={`mr-1 h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button
            size="sm"
            className="h-8 bg-[var(--scout-cyan)] text-primary hover:opacity-90"
            onClick={onFetchJobs}
            disabled={loading || extracting}
          >
            <BriefcaseBusiness className="mr-1 h-3.5 w-3.5" />
            {extracting ? "Fetching jobs…" : "Fetch jobs"}
          </Button>
        </div>
      </div>

      <DashboardOverview
        vacancyCount={vacancies.length}
        employerCount={employers.length}
        newVacancies24h={newVacancies24h}
        attentionCount={attentionCount}
        atsPerformance={atsPerformance}
      />

      <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyRecordsToolbar
            showArchived={showArchived}
            onShowArchivedChange={onShowArchivedChange}
            reviewFilter={reviewFilter}
            onReviewFilterChange={onReviewFilterChange}
            selectedEmployerId={selectedEmployerId}
            onEmployerChange={onEmployerChange}
            employers={employers}
            onRefresh={onRefresh}
            loading={loading}
          />
          <VacancyRecordList
            vacancies={filteredVacancies}
            loading={loading}
            selectedVacancyId={selectedVacancyId}
            openingVacancyId={openingVacancyId}
            onOpenVacancy={(vacancyId) => onOpenVacancy(vacancyId, visibleVacancies)}
          />
        </section>
        <section className="flex min-h-0 min-w-0 flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm">
          <VacancyDetailsPanel
            vacancy={selectedVacancy}
            loading={Boolean(openingVacancyId)}
            reviewReason={reviewReason}
            saving={vacancySaving}
            onChangeReviewReason={onChangeReviewReason}
            onClear={onClearSelection}
            onDecision={onDecision}
            onArchive={onArchive}
            onRestore={onRestore}
          />
        </section>
      </div>
    </section>
  );
}
