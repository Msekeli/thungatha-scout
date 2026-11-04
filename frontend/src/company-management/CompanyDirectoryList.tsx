import type { FC } from "react";
import type { Employer } from "../shared-contracts/employer-contracts";

type CompanyDirectoryListProps = {
  employers: Employer[];
  selectedEmployerId: string;
  onSelectEmployer: (employer: Employer) => void;
};

export const CompanyDirectoryList: FC<CompanyDirectoryListProps> = ({
  employers,
  selectedEmployerId,
  onSelectEmployer,
}) => {
  if (employers.length === 0) {
    return <div className="empty">No companies matched your criteria.</div>;
  }

  return (
    <div className="flex flex-col gap-1">
      {employers.map((employer) => (
        <button
          key={employer.id}
          type="button"
          className={`company-row ${selectedEmployerId === employer.id ? "selected" : ""}`}
          onClick={() => onSelectEmployer(employer)}
        >
          {employer.logo_url ? (
            <img src={employer.logo_url} alt={employer.name} className="employer-logo" />
          ) : (
            <span className="employer-avatar">{employer.name.slice(0, 1).toUpperCase()}</span>
          )}
          <span>
            <strong>{employer.name}</strong>
            <small>{employer.city || "Location not confirmed"}</small>
          </span>
          <span className="review-state text-[9px]">{employer.status.replace("_", " ")}</span>
        </button>
      ))}
    </div>
  );
};
