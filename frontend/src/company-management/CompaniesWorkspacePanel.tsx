import type { FormEvent } from "react";
import type {
  Employer,
  EmployerSource,
  ExtractionRun,
  GreenhouseInspection,
  Vacancy,
} from "../api";
import { CompanyAttentionActions } from "./CompanyAttentionActions";
import { CompanyDirectoryPanel } from "./CompanyDirectoryPanel";
import { CompanyProfilePanel } from "./CompanyProfilePanel";
import type { SourceDecisionDraft } from "../employer-sources/SourceReviewPanel";

type CompanyStatus = "approved" | "needs_review" | "rejected" | "inactive";

type CompaniesWorkspacePanelProps = {
  employers: Employer[];
  dashboardSources: EmployerSource[];
  selectedEmployer: Employer | null;
  vacancies: Vacancy[];
  selectedEmployerId: string;
  searchQuery: string;
  statusFilter: string;
  sources: EmployerSource[];
  extractionRuns: Record<string, ExtractionRun[]>;
  decisions: Record<string, SourceDecisionDraft>;
  logoUrl: string;
  logoSourceUrl: string;
  sourceUrl: string;
  editingSourceId: string | null;
  inspection: GreenhouseInspection | null;
  saving: boolean;
  inspecting: boolean;
  onSelectCompany: (employer: Employer) => void;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onAddCompany: () => void;
  onUpdateStatus: (status: CompanyStatus) => void;
  onDelete: () => void;
  onLogoUrlChange: (value: string) => void;
  onLogoSourceUrlChange: (value: string) => void;
  onSaveBranding: (event: FormEvent<HTMLFormElement>) => void;
  onEditSource: (source: EmployerSource) => void;
  onDecisionChange: (
    source: EmployerSource,
    field: keyof SourceDecisionDraft,
    value: string,
  ) => void;
  onSaveDecision: (source: EmployerSource) => void;
  onChangeSourceUrl: (value: string) => void;
  onInspect: () => void;
  onSaveSource: (event: FormEvent<HTMLFormElement>) => void;
  onCancelEdit: () => void;
};

export function CompaniesWorkspacePanel({
  employers,
  dashboardSources,
  selectedEmployer,
  vacancies,
  selectedEmployerId,
  searchQuery,
  statusFilter,
  sources,
  extractionRuns,
  decisions,
  logoUrl,
  logoSourceUrl,
  sourceUrl,
  editingSourceId,
  inspection,
  saving,
  inspecting,
  onSelectCompany,
  onSearchChange,
  onStatusFilterChange,
  onAddCompany,
  onUpdateStatus,
  onDelete,
  onLogoUrlChange,
  onLogoSourceUrlChange,
  onSaveBranding,
  onEditSource,
  onDecisionChange,
  onSaveDecision,
  onChangeSourceUrl,
  onInspect,
  onSaveSource,
  onCancelEdit,
}: CompaniesWorkspacePanelProps) {
  const jobsCount = selectedEmployer
    ? vacancies.filter((vacancy) => vacancy.employer_id === selectedEmployer.id).length
    : 0;

  return (
    <>
      <p className="mb-3 text-xs text-muted-foreground">
        Manage company identity, verification, branding and registered ATS sources.
      </p>
      <CompanyAttentionActions
        employers={employers}
        sources={dashboardSources}
        onSelectCompany={onSelectCompany}
      />
      <div className="grid min-h-0 gap-3 lg:grid-cols-[minmax(260px,0.8fr)_minmax(0,1.5fr)]">
        <CompanyDirectoryPanel
          employers={employers}
          selectedEmployerId={selectedEmployerId}
          searchQuery={searchQuery}
          statusFilter={statusFilter}
          onSearchChange={onSearchChange}
          onStatusFilterChange={onStatusFilterChange}
          onSelectEmployer={onSelectCompany}
          onAddCompany={onAddCompany}
        />
        <CompanyProfilePanel
          employer={selectedEmployer}
          jobsCount={jobsCount}
          sources={sources}
          extractionRuns={extractionRuns}
          decisions={decisions}
          logoUrl={logoUrl}
          logoSourceUrl={logoSourceUrl}
          sourceUrl={sourceUrl}
          editingSourceId={editingSourceId}
          inspection={inspection}
          saving={saving}
          inspecting={inspecting}
          onUpdateStatus={onUpdateStatus}
          onDelete={onDelete}
          onLogoUrlChange={onLogoUrlChange}
          onLogoSourceUrlChange={onLogoSourceUrlChange}
          onSaveBranding={onSaveBranding}
          onEditSource={onEditSource}
          onDecisionChange={onDecisionChange}
          onSaveDecision={onSaveDecision}
          onChangeSourceUrl={onChangeSourceUrl}
          onInspect={onInspect}
          onSaveSource={onSaveSource}
          onCancelEdit={onCancelEdit}
        />
      </div>
    </>
  );
}
