import type { LucideIcon } from "lucide-react";

type Props = {
  label: string;
  value: number;
  icon: LucideIcon;
};

export function DashboardMetricCard({ label, value, icon: Icon }: Props) {
  return (
    <div className="scout-vacancy-count-card">
      <span className="scout-vacancy-count-card__icon">
        <Icon className="h-4 w-4" aria-hidden="true" />
      </span>
      <div className="min-w-0">
        <p className="text-xs font-medium text-muted-foreground">{label}</p>
        <p className="text-xl font-bold leading-tight text-primary">{value.toLocaleString()}</p>
      </div>
    </div>
  );
}
