import type { FormEvent } from "react";
import type { Employer, EmployerSource, ExtractionRun, GreenhouseInspection } from "../api";
import { CompanyProfileActions } from "./CompanyProfileActions";
import { CompanyProfileHeader } from "./CompanyProfileHeader";
import { CompanyBrandingForm } from "./CompanyBrandingForm";
import { CompanySourcesSection } from "../employer-sources/CompanySourcesSection";
import type { SourceDecisionDraft } from "../employer-sources/SourceReviewPanel";

type CompanyStatus = "approved" | "needs_review" | "rejected" | "inactive";

type CompanyProfilePanelProps = {
  employer: Employer | null;
  jobsCount: number;
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

export function CompanyProfilePanel({
  employer,
  jobsCount,
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
}: CompanyProfilePanelProps) {
  return (
    <section className="min-w-0 rounded-xl border border-border bg-card p-4 shadow-sm">
      {employer ? (
        <>
          <CompanyProfileHeader
            employer={employer}
            jobsCount={jobsCount}
            sourcesCount={sources.length}
          />
          <CompanyProfileActions
            currentStatus={employer.status}
            saving={saving}
            onUpdateStatus={onUpdateStatus}
            onDelete={onDelete}
          />
          <CompanyBrandingForm
            logoUrl={logoUrl}
            logoSourceUrl={logoSourceUrl}
            saving={saving}
            onLogoUrlChange={onLogoUrlChange}
            onLogoSourceUrlChange={onLogoSourceUrlChange}
            onSubmit={onSaveBranding}
          />
          <CompanySourcesSection
            sources={sources}
            extractionRuns={extractionRuns}
            decisions={decisions}
            sourceUrl={sourceUrl}
            editingSourceId={editingSourceId}
            inspection={inspection}
            saving={saving}
            inspecting={inspecting}
            onEditSource={onEditSource}
            onDecisionChange={onDecisionChange}
            onSaveDecision={onSaveDecision}
            onChangeSourceUrl={onChangeSourceUrl}
            onInspect={onInspect}
            onSaveSource={onSaveSource}
            onCancelEdit={onCancelEdit}
          />
        </>
      ) : (
        <div className="grid min-h-[260px] content-center gap-2 px-6 text-center text-sm text-muted-foreground">
          <strong>Select a company</strong>
          <span>Choose a company to view its profile and registered job sources.</span>
        </div>
      )}
    </section>
  );
}
