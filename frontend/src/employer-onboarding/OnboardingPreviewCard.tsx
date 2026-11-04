import type { FC } from "react";
import type { CareersDiscovery } from "../shared-contracts/discovery-contracts";

type OnboardingPreviewCardProps = {
  discovery: CareersDiscovery | null;
};

export const OnboardingPreviewCard: FC<OnboardingPreviewCardProps> = ({
  discovery,
}) => {
  if (!discovery) return null;

  return (
    <div className="inspection-preview">
      <div className="flex items-center justify-between">
        <strong>{discovery.jobs.length} vacancies found</strong>
        <span className="review-state bg-emerald-100 text-emerald-800">
          Detected: {discovery.detected_adapter}
        </span>
      </div>
      <span>Board: {discovery.board_url}</span>
      <small>
        {discovery.complete
          ? "Vacancy preview is complete."
          : discovery.detail || "The preview is incomplete."}
      </small>
    </div>
  );
};
