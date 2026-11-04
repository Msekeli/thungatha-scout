import type { FC } from "react";
import type { Employer } from "../shared-contracts/employer-contracts";

type CompanyProfileHeaderProps = {
  employer: Employer;
  jobsCount: number;
  sourcesCount: number;
  onOpenBranding: () => void;
};

export const CompanyProfileHeader: FC<CompanyProfileHeaderProps> = ({
  employer,
  jobsCount,
  sourcesCount,
  onOpenBranding,
}) => {
  return (
    <div>
      <div className="section-heading">
        <div className="flex items-center gap-3">
          {employer.logo_url ? (
            <img src={employer.logo_url} alt={employer.name} className="employer-logo" />
          ) : (
            <span className="employer-avatar">{employer.name.slice(0, 1).toUpperCase()}</span>
          )}
          <div>
            <p className="eyebrow">COMPANY PROFILE</p>
            <h3 className="text-lg font-bold">{employer.name}</h3>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" className="button secondary" onClick={onOpenBranding}>
            Edit logo
          </button>
          <span className="review-state">{employer.status.replace("_", " ")}</span>
        </div>
      </div>

      <p className="profile-website">
        {employer.website_url ? (
          <a href={employer.website_url} target="_blank" rel="noreferrer" className="text-link">
            {employer.website_url} ↗
          </a>
        ) : (
          "Official website not supplied"
        )}
      </p>

      <div className="profile-stats">
        <div>
          <strong>{jobsCount}</strong>
          <span>Jobs collected</span>
        </div>
        <div>
          <strong>{sourcesCount}</strong>
          <span>Sources registered</span>
        </div>
      </div>
    </div>
  );
};
