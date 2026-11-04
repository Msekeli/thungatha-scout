import type { FC } from "react";
import type { Employer } from "../api";
import { Button } from "@/components/ui/button";
import { CompanyDirectoryList } from "./CompanyDirectoryList";
import { CompanySearchFilters } from "./CompanySearchFilters";

type CompanyDirectoryPanelProps = {
  employers: Employer[];
  selectedEmployerId: string;
  searchQuery: string;
  statusFilter: string;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onSelectEmployer: (employer: Employer) => void;
  onAddCompany: () => void;
};

export const CompanyDirectoryPanel: FC<CompanyDirectoryPanelProps> = ({
  employers,
  selectedEmployerId,
  searchQuery,
  statusFilter,
  onSearchChange,
  onStatusFilterChange,
  onSelectEmployer,
  onAddCompany,
}) => {
  const visibleEmployers = employers.filter(
    (employer) =>
      employer.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (statusFilter === "all" || employer.status === statusFilter),
  );

  return (
    <section className="min-w-0 rounded-xl border border-border bg-card p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between gap-3 border-b border-border pb-3">
        <div className="flex items-center gap-3">
          <h3>Registered companies</h3>
          <span>
            {visibleEmployers.length} / {employers.length}
          </span>
        </div>
        <Button
          type="button"
          className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
          onClick={onAddCompany}
        >
          + Add company
        </Button>
      </div>
      <CompanySearchFilters
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        statusFilter={statusFilter}
        onStatusFilterChange={onStatusFilterChange}
      />
      <CompanyDirectoryList
        employers={visibleEmployers}
        selectedEmployerId={selectedEmployerId}
        onSelectEmployer={onSelectEmployer}
        emptyMessage={
          employers.length ? "No companies match these filters." : "No companies registered."
        }
      />
    </section>
  );
};
