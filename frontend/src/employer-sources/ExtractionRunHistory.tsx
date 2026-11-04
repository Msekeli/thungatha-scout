import type { FC } from "react";
import type { ExtractionRun } from "../shared-contracts/vacancy-contracts";

type ExtractionRunHistoryProps = {
  runs: ExtractionRun[];
};

export const ExtractionRunHistory: FC<ExtractionRunHistoryProps> = ({
  runs,
}) => {
  if (runs.length === 0) {
    return <p className="text-xs text-slate-500">No extraction runs recorded yet.</p>;
  }

  const latestRun = runs[0];

  return (
    <div className="run-history">
      <div className="run-heading">
        <strong>Latest extraction</strong>
        <span>{runs.length} recorded run(s)</span>
      </div>

      <div className="run-summary">
        <span className={`run-outcome ${latestRun.outcome}`}>
          {latestRun.outcome.replace("_", " ")}
        </span>
        <span className="ml-2">
          {latestRun.jobs_received} received · {latestRun.jobs_inserted} new ·{" "}
          {latestRun.jobs_updated} updated
        </span>
        <span className="ml-2 text-slate-400">
          {latestRun.complete ? "Complete" : "Incomplete"}
        </span>
      </div>

      {latestRun.detail && <p className="run-detail">{latestRun.detail}</p>}

      <div className="run-meta">
        <span>
          Started:{" "}
          {latestRun.started_at
            ? new Date(latestRun.started_at).toLocaleString()
            : "Unknown"}
        </span>
        <span>
          Finished:{" "}
          {latestRun.finished_at
            ? new Date(latestRun.finished_at).toLocaleString()
            : "In progress"}
        </span>
      </div>

      {runs.length > 1 && (
        <details className="mt-2 text-xs">
          <summary className="cursor-pointer font-semibold text-slate-600">
            Previous runs ({runs.length - 1})
          </summary>
          <div className="mt-1 divide-y divide-slate-200">
            {runs.slice(1).map((run) => (
              <div key={run.id} className="older-run">
                <strong>{run.outcome.replace("_", " ")}</strong>
                <span>
                  {run.jobs_received} received · {run.jobs_inserted} new ·{" "}
                  {run.jobs_updated} updated
                </span>
                <small>{run.detail || "No additional detail"}</small>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
};
