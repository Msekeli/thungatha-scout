import type { FC } from "react";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Employer } from "../api";

type Props = {
  employer: Employer;
  careersUrl: string | null;
  jobsCount: number;
  sourcesCount: number;
  latestJobs: number | null;
  previousJobs: number | null;
  lastRunAt: string | null;
};

export const CompanyProfileHeader: FC<Props> = ({
  employer,
  careersUrl,
  jobsCount,
  sourcesCount,
  latestJobs,
  previousJobs,
  lastRunAt,
}) => {
  const delta = latestJobs !== null && previousJobs !== null ? latestJobs - previousJobs : null;
  const changeLabel =
    delta === null
      ? "Comparison unavailable"
      : delta > 0
        ? `+${delta} jobs since previous run`
        : delta < 0
          ? `${delta} jobs since previous run`
          : "No change since previous run";
  return (
    <div className="scout-company-profile-header">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="scout-company-eyebrow">COMPANY PROFILE</p>
          <h3 className="mt-1 truncate text-base font-bold scout-company-heading">
            {employer.name}
          </h3>
          <p className="mt-1 break-all text-[11px] scout-company-muted">
            {careersUrl ? (
              <a
                href={careersUrl}
                target="_blank"
                rel="noreferrer"
                className="scout-company-link underline-offset-2 hover:underline"
              >
                {careersUrl}
              </a>
            ) : (
              "Official careers link not recorded"
            )}
          </p>
        </div>
        <Badge
          variant="outline"
          className={`scout-status ${employer.status === "approved" ? "scout-status--approved" : employer.status === "rejected" ? "scout-status--rejected" : "scout-status--review"}`}
        >
          {employer.status.replaceAll("_", " ")}
        </Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 border-t pt-3 sm:grid-cols-3 scout-company-divider">
        <Metric value={jobsCount} label="Current jobs" />
        <Metric value={latestJobs ?? "—"} label="Latest run jobs" />
        {delta !== null && delta !== 0 && (
          <div className="scout-company-metric">
            <div className="flex items-center gap-1 text-sm font-semibold">
              {delta > 0 ? (
                <ArrowUpRight className="h-4 w-4 scout-metric-positive" />
              ) : (
                <ArrowDownRight className="h-4 w-4 scout-metric-negative" />
              )}
              <span>{delta > 0 ? `+${delta}` : delta}</span>
            </div>
            <span className="text-[10px] scout-company-muted">{changeLabel}</span>
          </div>
        )}
      </div>
      <p className="mt-3 text-[10px] scout-company-muted">
        {sourcesCount} registered source{sourcesCount === 1 ? "" : "s"}
        {lastRunAt ? ` · Last run ${new Date(lastRunAt).toLocaleString()}` : ""}
      </p>
    </div>
  );
};

function Metric({ value, label }: { value: number | string; label: string }) {
  return (
    <div className="scout-company-metric">
      <strong className="text-base font-bold scout-company-heading">{value}</strong>
      <p className="text-[10px] scout-company-muted">{label}</p>
    </div>
  );
}
