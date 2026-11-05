import type { FC } from "react";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { CompanyDirectoryList } from "./CompanyDirectoryList";
import { CompanyDirectoryToolbar } from "./CompanyDirectoryToolbar";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  selectedEmployerId: string;
  searchQuery: string;
  sourceFilter: string;
  extractionRuns: Record<string, ExtractionRun[]>;
  onSearchChange: (value: string) => void;
  onSourceFilterChange: (value: string) => void;
  onSelectEmployer: (employer: Employer) => void;
  onAddCompany: () => void;
};

export const CompanyDirectoryPanel: FC<Props> = (props) => {
  const visible = props.employers.filter(
    (item) =>
      item.name.toLowerCase().includes(props.searchQuery.toLowerCase()) &&
      (props.sourceFilter === "all" ||
        props.sources.some(
          (source) => source.employer_id === item.id && source.adapter_key === props.sourceFilter,
        )),
  );
  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden scout-company-directory">
      <CompanyDirectoryToolbar
        searchQuery={props.searchQuery}
        sourceFilter={props.sourceFilter}
        onSearchChange={props.onSearchChange}
        onSourceFilterChange={props.onSourceFilterChange}
        onAddCompany={props.onAddCompany}
      />
      <div className="mb-3 flex items-center justify-between text-xs scout-company-muted">
        <span>
          Showing <strong className="scout-company-count">{visible.length}</strong> of{" "}
          {props.employers.length} employers
        </span>
        <span className="hidden sm:inline">Select a card to manage its sources and details</span>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        <CompanyDirectoryList
          employers={visible}
          sources={props.sources}
          extractionRuns={props.extractionRuns}
          selectedEmployerId={props.selectedEmployerId}
          onSelectEmployer={props.onSelectEmployer}
          emptyMessage={
            props.employers.length
              ? "No companies match your search."
              : "No companies registered yet."
          }
        />
      </div>
    </section>
  );
};
