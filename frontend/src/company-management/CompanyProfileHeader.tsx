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
    <div className="mb-4 rounded-xl border border-slate-700 bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/60 p-4 text-white shadow-lg shadow-black/20">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold tracking-widest text-cyan-300">COMPANY PROFILE</p>
          <h3 className="mt-1 truncate text-base font-bold text-white">{employer.name}</h3>
          <p className="mt-1 break-all text-[11px] text-slate-400">
            {careersUrl ? (
              <a
                href={careersUrl}
                target="_blank"
                rel="noreferrer"
                className="text-cyan-300 underline-offset-2 hover:text-cyan-100 hover:underline"
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
          className="shrink-0 border-slate-600 bg-slate-800 text-slate-200 capitalize"
        >
          {employer.status.replaceAll("_", " ")}
        </Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 border-t border-slate-700 pt-3 sm:grid-cols-3">
        <Metric value={jobsCount} label="Current jobs" />
        <Metric value={latestJobs ?? "—"} label="Latest run jobs" />
        {delta !== null && delta !== 0 && (
          <div className="rounded-lg border border-slate-700 bg-slate-950/70 p-2">
            <div className="flex items-center gap-1 text-sm font-semibold">
              {delta > 0 ? (
                <ArrowUpRight className="h-4 w-4 text-emerald-500" />
              ) : (
                <ArrowDownRight className="h-4 w-4 text-amber-500" />
              )}
              <span>{delta > 0 ? `+${delta}` : delta}</span>
            </div>
            <span className="text-[10px] text-slate-400">{changeLabel}</span>
          </div>
        )}
      </div>
      <p className="mt-3 text-[10px] text-slate-400">
        {sourcesCount} registered source{sourcesCount === 1 ? "" : "s"}
        {lastRunAt ? ` · Last run ${new Date(lastRunAt).toLocaleString()}` : ""}
      </p>
    </div>
  );
};

function Metric({ value, label }: { value: number | string; label: string }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/70 p-2">
      <strong className="text-base font-bold text-white">{value}</strong>
      <p className="text-[10px] text-slate-400">{label}</p>
    </div>
  );
}
