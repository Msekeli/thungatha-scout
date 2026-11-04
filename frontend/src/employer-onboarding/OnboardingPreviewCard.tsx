import { Badge } from "@/components/ui/badge";
import type { CareersDiscovery } from "../api";

type OnboardingPreviewCardProps = {
  discovery: CareersDiscovery | null;
};

export function OnboardingPreviewCard({ discovery }: OnboardingPreviewCardProps) {
  if (!discovery) return null;

  return (
    <div className="grid gap-2 rounded-lg border border-border bg-muted/50 p-3 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <strong className="font-semibold text-foreground">
          {discovery.jobs.length} vacancies found
        </strong>
        <Badge variant="outline" className="capitalize">
          Detected: {discovery.detected_adapter}
        </Badge>
      </div>
      <span className="break-all text-muted-foreground">Board: {discovery.board_url}</span>
      <small className="text-muted-foreground">
        {discovery.complete
          ? "Vacancy preview is complete."
          : discovery.detail || "The preview is incomplete."}
      </small>
    </div>
  );
}
