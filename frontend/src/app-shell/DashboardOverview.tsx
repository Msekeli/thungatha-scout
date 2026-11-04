import { Activity, BriefcaseBusiness, Building2, CircleAlert, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";

type Props = {
  vacancyCount: number;
  employerCount: number;
  newVacancies24h: number;
  attentionCount: number;
  atsPerformance: ReturnType<typeof useScoutDashboardMetrics>["atsPerformance"];
};

export function DashboardOverview(props: Props) {
  const metrics = [
    ["Collected vacancies", props.vacancyCount, "Active records", BriefcaseBusiness, "text-accent-foreground", "bg-accent"],
    ["Registered companies", props.employerCount, "Employer records", Building2, "text-secondary-foreground", "bg-secondary"],
    ["New in last 24 hours", props.newVacancies24h, "Based on first seen time", Sparkles, "text-success", "bg-success-surface"],
    ["Needs admin attention", props.attentionCount, "Pending or needs verification", CircleAlert, "text-warning", "bg-warning-surface"],
  ] as const;

  return (
    <>
      <div className="grid grid-cols-2 gap-2 xl:grid-cols-4">
        {metrics.map(([label, value, note, Icon, color, bg]) => (
          <div key={label} className="flex items-center gap-3 rounded-xl border border-border bg-card p-3 shadow-sm">
            <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ${bg} ${color}`}>
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
          <h3 className="flex items-center gap-2 text-xs font-bold text-primary">
            <Activity className="h-4 w-4 text-scout-cyan" /> ATS performance
          </h3>
          <span className="text-right text-[10px] text-muted-foreground">
            Source health and latest extraction results
          </span>
        </div>
        <div className="grid gap-2 md:grid-cols-2">
          {props.atsPerformance.map((item) => (
            <div key={item.adapter} className="flex items-center justify-between gap-3 rounded-lg border border-border bg-background px-3 py-2">
              <div className="min-w-0">
                <p className="text-xs font-bold capitalize text-foreground">{item.adapter}</p>
                <p className="text-[10px] text-muted-foreground">
                  {item.sourceCount} sources · {item.verified} verified · {item.jobCount} vacancies
                </p>
              </div>
              <div className="text-right">
                <Badge variant={item.latest && ["success", "empty"].includes(item.latest.outcome)
                  ? "default" : item.latest && item.latest.outcome !== "running" ? "destructive" : "secondary"}
                  className={item.latest && ["success", "empty"].includes(item.latest.outcome)
                    ? "border-transparent bg-scout-cyan text-scout-navy hover:bg-scout-cyan"
                    : item.latest?.outcome === "running" || !item.latest
                      ? "border-border bg-secondary text-secondary-foreground hover:bg-secondary" : "capitalize"}>
                  {item.latest?.outcome ?? "No runs"}
                </Badge>
                <p className="mt-1 text-[10px] text-muted-foreground">
                  {item.latest ? `${item.latest.jobs_inserted} new · ${item.failed} failed runs` : "Awaiting first extraction"}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
