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
          Greenhouse board resolved
        </strong>
        <Badge variant="outline">Greenhouse</Badge>
      </div>
      <span className="text-muted-foreground">Board name: {discovery.board_name}</span>
      <span className="break-all text-muted-foreground">Board: {discovery.board_url}</span>
      <small className="text-muted-foreground">
        Register the company to start vacancy extraction. Employer/source verification remains a separate step.
      </small>
    </div>
  );
}
