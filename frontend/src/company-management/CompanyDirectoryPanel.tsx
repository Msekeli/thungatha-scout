import type { FC } from "react";
import type { Employer, EmployerSource } from "../api";
import { CompanyDirectoryList } from "./CompanyDirectoryList";
import { CompanyDirectoryToolbar } from "./CompanyDirectoryToolbar";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  selectedEmployerId: string;
  searchQuery: string;
  statusFilter: string;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onSelectEmployer: (employer: Employer) => void;
  onAddCompany: () => void;
};

export const CompanyDirectoryPanel: FC<Props> = (props) => {
  const visible = props.employers.filter(
    (item) =>
      item.name.toLowerCase().includes(props.searchQuery.toLowerCase()) &&
      (props.statusFilter === "all" || item.status === props.statusFilter),
  );
  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden scout-company-directory">
      <CompanyDirectoryToolbar
        count={props.employers.length}
        searchQuery={props.searchQuery}
        statusFilter={props.statusFilter}
        onSearchChange={props.onSearchChange}
        onStatusFilterChange={props.onStatusFilterChange}
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
