import type { FC } from "react";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { CompanyDirectoryCard } from "./CompanyDirectoryCard";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  extractionRuns: Record<string, ExtractionRun[]>;
  selectedEmployerId: string;
  onSelectEmployer: (employer: Employer) => void;
  emptyMessage?: string;
};

export const CompanyDirectoryList: FC<Props> = ({
  employers,
  sources,
  extractionRuns,
  selectedEmployerId,
  onSelectEmployer,
  emptyMessage = "No companies matched your criteria.",
}) => {
  if (!employers.length)
    return (
      <div className="rounded-xl border border-dashed border-border py-12 text-center text-sm text-muted-foreground">
        {emptyMessage}
      </div>
    );
  return (
    <div className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
      {employers.map((employer) => (
        <CompanyDirectoryCard
          key={employer.id}
          employer={employer}
          sources={sources.filter((source) => source.employer_id === employer.id)}
          extractionRuns={extractionRuns}
          selected={selectedEmployerId === employer.id}
          onSelect={onSelectEmployer}
        />
      ))}
    </div>
  );
};
