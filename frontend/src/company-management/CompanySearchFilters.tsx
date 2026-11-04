import type { FC } from "react";

type CompanySearchFiltersProps = {
  searchQuery: string;
  onSearchChange: (value: string) => void;
  statusFilter: string;
  onStatusFilterChange: (value: string) => void;
};

export const CompanySearchFilters: FC<CompanySearchFiltersProps> = ({
  searchQuery,
  onSearchChange,
  statusFilter,
  onStatusFilterChange,
}) => {
  return (
    <div className="company-filters">
      <input
        type="search"
        value={searchQuery}
        onChange={(event) => onSearchChange(event.target.value)}
        placeholder="Search registered companies…"
        aria-label="Search companies"
      />
      <select
        value={statusFilter}
        onChange={(event) => onStatusFilterChange(event.target.value)}
        aria-label="Filter companies by status"
      >
        <option value="all">All statuses</option>
        <option value="discovered">Discovered</option>
        <option value="approved">Approved</option>
        <option value="needs_review">Needs review</option>
        <option value="rejected">Rejected</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>
  );
};
