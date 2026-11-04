import type { FC } from "react";
import type { Employer } from "../shared-contracts/employer-contracts";

type VacancyFiltersProps = {
  employers: Employer[];
  selectedEmployerId: string;
  onSelectEmployerId: (id: string) => void;
  reviewFilter: string;
  onSelectReviewFilter: (status: string) => void;
  showArchived: boolean;
  onToggleArchived: () => void;
  onRefresh: () => void;
  loading: boolean;
};

export const VacancyFilters: FC<VacancyFiltersProps> = ({
  employers,
  selectedEmployerId,
  onSelectEmployerId,
  reviewFilter,
  onSelectReviewFilter,
  showArchived,
  onToggleArchived,
  onRefresh,
  loading,
}) => {
  return (
    <div className="jobs-toolbar">
      <div>
        <h3>{showArchived ? "Archived vacancies" : "All vacancies"}</h3>
        <p className="muted">Filter vacancies by company or verification status.</p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <select
          aria-label="Filter jobs by company"
          value={selectedEmployerId}
          onChange={(event) => onSelectEmployerId(event.target.value)}
        >
          <option value="all">All companies</option>
          {employers.map((employer) => (
            <option key={employer.id} value={employer.id}>
              {employer.name}
            </option>
          ))}
        </select>
        <select
          aria-label="Filter jobs by review status"
          value={reviewFilter}
          onChange={(event) => onSelectReviewFilter(event.target.value)}
        >
          <option value="all">All review statuses</option>
          <option value="needs_verification">Needs verification</option>
          <option value="verified">Verified</option>
          <option value="rejected">Rejected</option>
          <option value="pending">Pending</option>
        </select>
        <button
          type="button"
          className={`button ${showArchived ? "primary" : "secondary"}`}
          onClick={onToggleArchived}
        >
          {showArchived ? "Show active" : "View archive"}
        </button>
        <button type="button" className="button secondary" onClick={onRefresh} disabled={loading}>
          Refresh
        </button>
      </div>
    </div>
  );
};
