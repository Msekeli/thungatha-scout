import { BriefcaseBusiness, Building2, CircleAlert, Sparkles } from "lucide-react";

type Props = {
  vacancyCount: number;
  employerCount: number;
  newVacancies24h: number;
  attentionCount: number;
};

export function DashboardMetricCards(props: Props) {
  const metrics = [
    ["Collected vacancies", props.vacancyCount, "Active records", BriefcaseBusiness, "text-accent-foreground", "bg-accent"],
    ["Registered companies", props.employerCount, "Employer records", Building2, "text-secondary-foreground", "bg-secondary"],
    ["New in last 24 hours", props.newVacancies24h, "Based on first seen time", Sparkles, "text-success", "bg-success-surface"],
    ["Needs admin attention", props.attentionCount, "Pending or needs verification", CircleAlert, "text-warning", "bg-warning-surface"],
  ] as const;

  return (
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
  );
}
