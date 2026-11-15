import {
  Activity,
  AlertTriangle,
  Building2,
  CheckCircle2,
  Play,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource, ExtractionRun } from "../api";
import { SourceStatusPanel } from "./SourceStatusPanel";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  runs: Record<string, ExtractionRun[]>;
  running: boolean;
  refreshing: boolean;
  onRunNow: () => void;
  onRefresh: () => void;
};

type MetricCardProps = {
  label: string;
  value: number;
  icon: typeof Building2;
};

const failedOutcomes = [
  "transient_failure",
  "persistence_failure",
  "failed",
  "http_failure",
];
const blockedOutcomes = ["blocked", "rate_limited"];
const isSuccessful = (run: ExtractionRun) =>
  run.complete && ["success", "empty"].includes(run.outcome);
const needsAttention = (run: ExtractionRun) =>
  failedOutcomes.includes(run.outcome) ||
  blockedOutcomes.includes(run.outcome) ||
  !isSuccessful(run);

function MetricCard({ label, value, icon: Icon }: MetricCardProps) {
  return (
    <div className="scout-vacancy-count-card">
      <span className="scout-vacancy-count-card__icon">
        <Icon className="h-4 w-4" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <p className="text-xl font-bold leading-tight text-primary">
          {value.toLocaleString()}
        </p>
      </div>
    </div>
  );
}

export function IngestionOperationsPanel({
  employers,
  sources,
  runs,
  running,
  refreshing,
  onRunNow,
  onRefresh,
}: Props) {
  const allRuns = Object.values(runs).flat();
  const successfulRuns = allRuns.filter(isSuccessful).length;
  const attentionRuns = allRuns.filter(needsAttention).length;

  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 py-4">
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Operations dashboard</h2>
          <p className="text-sm text-muted-foreground">
            Monitor employer sources, retrieval health and recent activity.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="border-input bg-background text-primary"
            onClick={onRefresh}
            disabled={refreshing || running}
          >
            <RefreshCw
              className={
                refreshing ? "mr-2 h-4 w-4 animate-spin" : "mr-2 h-4 w-4"
              }
            />
            Refresh
          </Button>
          <Button
            className="bg-scout-cyan text-scout-navy hover:brightness-95"
            onClick={onRunNow}
            disabled={running || !sources.length}
          >
            <Play className="mr-2 h-4 w-4" />
            {running ? "Retrieval running…" : "Run retrieval"}
          </Button>
        </div>
      </div>

      <div className="grid shrink-0 grid-cols-2 gap-2 xl:grid-cols-4">
        <MetricCard
          label="Registered employers"
          value={employers.length}
          icon={Building2}
        />
        <MetricCard
          label="Configured sources"
          value={sources.length}
          icon={Activity}
        />
        <MetricCard
          label="Successful runs"
          value={successfulRuns}
          icon={CheckCircle2}
        />
        <MetricCard
          label="Runs needing attention"
          value={attentionRuns}
          icon={AlertTriangle}
        />
      </div>
      <p className="shrink-0 text-xs text-muted-foreground">
        Run metrics reflect the retrieval history currently loaded for each source.
      </p>

      <SourceStatusPanel employers={employers} sources={sources} runs={runs} />
    </section>
  );
}
