import { Activity, BriefcaseBusiness, Building2, CircleAlert, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";

type DashboardOverviewProps = {
  vacancyCount: number;
  employerCount: number;
  newVacancies24h: number;
  attentionCount: number;
  atsPerformance: ReturnType<typeof useScoutDashboardMetrics>["atsPerformance"];
};

export function DashboardOverview({
  vacancyCount,
  employerCount,
  newVacancies24h,
  attentionCount,
  atsPerformance,
}: DashboardOverviewProps) {
  const metrics = [
    {
      label: "Collected vacancies",
      value: vacancyCount,
      note: "Active records",
      icon: BriefcaseBusiness,
      color: "text-accent-foreground",
      bg: "bg-accent",
    },
    {
      label: "Registered companies",
      value: employerCount,
      note: "Employer records",
      icon: Building2,
      color: "text-secondary-foreground",
      bg: "bg-secondary",
    },
    {
      label: "New in last 24 hours",
      value: newVacancies24h,
      note: "Based on first seen time",
      icon: Sparkles,
      color: "text-success",
      bg: "bg-success-surface",
    },
    {
      label: "Needs admin attention",
      value: attentionCount,
      note: "Pending or needs verification",
      icon: CircleAlert,
      color: "text-warning",
      bg: "bg-warning-surface",
    },
  ];

  return (
    <>
      <div className="grid grid-cols-2 gap-2 xl:grid-cols-4">
        {metrics.map(({ label, value, note, icon: Icon, color, bg }) => (
          <div
            key={label}
            className="flex items-center gap-3 rounded-xl border border-border bg-card p-3 shadow-sm"
          >
            <span
              className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${bg} ${color}`}
            >
              <Icon className="h-5 w-5" />
            </span>
            <div className="min-w-0">
              <p className="text-[11px] font-medium text-muted-foreground">{label}</p>
              <p className="text-xl font-bold leading-tight text-primary">{value}</p>
              <p className="text-[10px] text-muted-foreground/70">{note}</p>
            </div>
          </div>
        ))}
      </div>

      <section className="rounded-xl border border-white/80 bg-card p-3 text-card-foreground shadow-lg shadow-black/20">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-xs font-bold text-white">
            <Activity className="h-4 w-4 text-scout-cyan" /> ATS performance
          </h3>
          <span className="text-right text-[10px] text-muted-foreground">
            Source health and latest extraction results
          </span>
        </div>
        <div className="grid gap-2 md:grid-cols-2">
          {atsPerformance.map((item) => (
            <div
              key={item.adapter}
              className="flex items-center justify-between gap-3 rounded-lg border border-border bg-background px-3 py-2"
            >
              <div className="min-w-0">
                <p className="text-xs font-bold capitalize text-foreground">{item.adapter}</p>
                <p className="text-[10px] text-muted-foreground">
                  {item.sourceCount} sources · {item.verified} verified · {item.jobCount} vacancies
                </p>
              </div>
              <div className="text-right">
                <Badge
                  variant={
                    item.latest && ["success", "empty"].includes(item.latest.outcome)
                      ? "default"
                      : item.latest && item.latest.outcome !== "running"
                        ? "destructive"
                        : "secondary"
                  }
                  className={
                    item.latest && ["success", "empty"].includes(item.latest.outcome)
                      ? "border-transparent bg-scout-cyan text-scout-navy hover:bg-scout-cyan"
                      : item.latest?.outcome === "running" || !item.latest
                        ? "border-border bg-secondary text-secondary-foreground hover:bg-secondary"
                        : "capitalize"
                  }
                >
                  {item.latest?.outcome ?? "No runs"}
                </Badge>
                <p className="mt-1 text-[10px] text-muted-foreground">
                  {item.latest
                    ? `${item.latest.jobs_inserted} new · ${item.failed} failed runs`
                    : "Awaiting first extraction"}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
