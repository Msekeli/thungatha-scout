import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { useScoutDashboardMetrics } from "../useScoutDashboardMetrics";
import { DashboardMetricCards } from "./DashboardMetricCards";

type Props = {
  vacancyCount: number;
  employerCount: number;
  newVacancies24h: number;
  attentionCount: number;
  atsPerformance: ReturnType<typeof useScoutDashboardMetrics>["atsPerformance"];
};

export function DashboardOverview(props: Props) {
  return (
    <>
      <DashboardMetricCards
        vacancyCount={props.vacancyCount}
        employerCount={props.employerCount}
        newVacancies24h={props.newVacancies24h}
        attentionCount={props.attentionCount}
      />
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
