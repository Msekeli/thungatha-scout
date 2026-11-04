import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";

type CompanyAttentionActionsProps = {
  employers: Employer[];
  sources: EmployerSource[];
  onSelectCompany: (employer: Employer) => void;
};

export function CompanyAttentionActions({
  employers,
  sources,
  onSelectCompany,
}: CompanyAttentionActionsProps) {
  const discovered = employers.filter((employer) => employer.status === "discovered");
  const needsReview = employers.filter((employer) => employer.status === "needs_review");
  const uncheckedSources = sources.filter(
    (source) => source.status !== "verified" || source.permission_status !== "allowed",
  );
  const firstUncheckedSource = uncheckedSources[0];
  const uncheckedEmployer = firstUncheckedSource
    ? employers.find((employer) => employer.id === firstUncheckedSource.employer_id)
    : undefined;

  return (
    <section className="mb-3 grid gap-2 rounded-xl border border-scout-navy bg-scout-navy p-3 shadow-md md:grid-cols-3">
      <div>
        <p className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground/70">
          Suggested actions
        </p>
        <p className="mt-1 text-xs text-white/70">
          Work through these records to keep the company directory and sources reliable.
        </p>
      </div>
      <Button
        type="button"
        variant="ghost"
        className="h-auto w-full flex-col items-start justify-center rounded-lg border border-border bg-warning-surface px-3 py-2 text-left shadow-none hover:bg-warning-surface hover:opacity-90"
        onClick={() => discovered[0] && onSelectCompany(discovered[0])}
        disabled={discovered.length === 0}
      >
        <strong className="block text-sm text-warning">
          {discovered.length} awaiting approval
        </strong>
        <span className="text-[10px] text-warning">Review new company records</span>
      </Button>
      <Button
        type="button"
        variant="ghost"
        className="h-auto w-full flex-col items-start justify-center rounded-lg border border-border bg-warning-surface px-3 py-2 text-left shadow-none hover:bg-warning-surface hover:opacity-90"
        onClick={() => needsReview[0] && onSelectCompany(needsReview[0])}
        disabled={needsReview.length === 0}
      >
        <strong className="block text-sm text-warning">
          {needsReview.length} flagged for review
        </strong>
        <span className="text-[10px] text-warning">Resolve company identity concerns</span>
      </Button>
      <Button
        type="button"
        variant="ghost"
        className="h-auto w-full flex-col items-start justify-center rounded-lg border border-border bg-card px-3 py-2 text-left shadow-none transition-colors hover:bg-accent"
        onClick={() => uncheckedEmployer && onSelectCompany(uncheckedEmployer)}
        disabled={!uncheckedEmployer}
      >
        <strong className="block text-sm text-foreground">
          {uncheckedSources.length} sources need checks
        </strong>
        <span className="text-[10px] text-muted-foreground">
          Verify source and permission status
        </span>
      </Button>
    </section>
  );
}
