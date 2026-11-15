import { ArrowDownRight, ArrowUpRight } from "lucide-react";

export type RunSummary = {
  added: number;
  missing: number;
  net: number;
  companies: { name: string; added: number; missing: number; baseline: boolean }[];
  baselineCount: number;
};

type Props = { summary: RunSummary | null; extracting: boolean };

export function DashboardRunSummary({ summary, extracting }: Props) {
  if (extracting) return <span className="text-xs text-muted-foreground">Crawler running…</span>;
  if (!summary) return null;
  return (
    <div className="flex flex-wrap items-center gap-2 text-xs" aria-live="polite">
      <span className="font-semibold">Latest completed run:</span>
      <span className="inline-flex items-center gap-1 text-muted-foreground">
        <ArrowUpRight className="h-3 w-3" /> +{summary.added} added
      </span>
      <span className="inline-flex items-center gap-1 text-muted-foreground">
        <ArrowDownRight className="h-3 w-3" /> −{summary.missing} missing
      </span>
      <span className="text-muted-foreground">
        Net {summary.net >= 0 ? "+" : ""}
        {summary.net}
      </span>
      {summary.baselineCount > 0 && (
        <span className="text-muted-foreground">
          Initial collection:{" "}
          {summary.companies
            .filter((item) => item.baseline)
            .map((item) => item.name)
            .join(", ")}
        </span>
      )}
      {summary.companies
        .filter((item) => item.added || item.missing)
        .map((item) => (
          <span key={item.name} className="text-muted-foreground">
            {item.name}: +{item.added}/−{item.missing}
          </span>
        ))}
    </div>
  );
}
