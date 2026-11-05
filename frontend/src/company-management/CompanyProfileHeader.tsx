import type { FC } from "react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Employer, ExtractionRun } from "../api";

type Props = {
  employer: Employer;
  jobsCount: number;
  sourcesCount: number;
  latestRun?: ExtractionRun;
  previousRun?: ExtractionRun;
};

export const CompanyProfileHeader: FC<Props> = ({
  employer, jobsCount, sourcesCount, latestRun, previousRun,
}) => {
  const delta = latestRun && previousRun
    ? latestRun.jobs_received - previousRun.jobs_received : null;
  const changeLabel = delta === null ? "No comparison yet"
    : delta > 0 ? `+${delta} jobs since previous run`
    : delta < 0 ? `${delta} jobs since previous run` : "No change since previous run";
  return (
    <div className="mb-4 rounded-xl border border-border bg-gradient-to-br from-card via-card to-primary/10 p-4 text-foreground shadow-md shadow-black/10">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold tracking-widest text-primary">COMPANY PROFILE</p>
          <h3 className="mt-1 truncate text-base font-bold text-foreground">{employer.name}</h3>
          <p className="mt-1 break-all text-[11px] text-muted-foreground">
            {employer.website_url ? (
              <a href={employer.website_url} target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-1 text-primary underline-offset-2 hover:underline">
                {employer.website_url}
              </a>
            ) : "Official website not supplied"}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            {[employer.city, employer.province, employer.country].filter(Boolean).join(", ") ||
              "Location not recorded"}
          </p>
        </div>
        <Badge variant="outline" className="shrink-0 border-border text-foreground capitalize">
          {employer.status.replaceAll("_", " ")}
        </Badge>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3 border-t border-border pt-3 sm:grid-cols-3">
        <Metric value={jobsCount} label="Current jobs" />
        <Metric value={latestRun?.jobs_received ?? "—"} label="Latest run jobs" />
        <div className="rounded-lg bg-background/70 p-2">
          <div className="flex items-center gap-1 text-sm font-semibold">
            {delta === null || delta === 0 ? <Minus className="h-4 w-4 text-muted-foreground" />
              : delta > 0 ? <ArrowUpRight className="h-4 w-4 text-emerald-500" />
              : <ArrowDownRight className="h-4 w-4 text-amber-500" />}
            <span>{delta === null ? "—" : delta > 0 ? `+${delta}` : delta}</span>
          </div>
          <span className="text-[10px] text-muted-foreground">{changeLabel}</span>
        </div>
      </div>
      <p className="mt-3 text-[10px] text-muted-foreground">
        {sourcesCount} registered source{sourcesCount === 1 ? "" : "s"}
        {latestRun?.finished_at ? ` · Last run ${new Date(latestRun.finished_at).toLocaleString()}` : ""}
      </p>
    </div>
  );
};

function Metric({ value, label }: { value: number | string; label: string }) {
  return (
    <div className="rounded-lg bg-background/70 p-2">
      <strong className="text-base font-bold text-foreground">{value}</strong>
      <p className="text-[10px] text-muted-foreground">{label}</p>
    </div>
  );
}
