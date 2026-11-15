import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

export type RunSummary = {
  added: number;
  missing: number;
  net: number;
  baselineSources: number;
  sourceCount: number;
  companies: {
    name: string;
    added: number;
    missing: number;
    baselineSources: number;
    sourceCount: number;
  }[];
};

type Props = { summary: RunSummary | null; extracting: boolean };

const addedStyle =
  "inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2.5 py-1 font-semibold text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300";
const missingStyle =
  "inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 font-semibold text-amber-800 dark:bg-amber-950 dark:text-amber-300";

export function DashboardRunSummary({ summary, extracting }: Props) {
  if (extracting) return <span className="text-xs text-muted-foreground">Crawler running…</span>;
  if (!summary) return null;

  const changedCompanies = summary.companies.filter((company) => company.added || company.missing);
  return (
    <section className="space-y-2 rounded-lg border bg-card p-3" aria-live="polite">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-sm font-semibold">Collection changes</h3>
          <p className="text-xs text-muted-foreground">
            Latest completed result recorded for each of {summary.sourceCount} sources
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className={addedStyle}>
            <ArrowUpRight className="h-3.5 w-3.5" />
            {summary.added} added
          </span>
          <span className={missingStyle}>
            <ArrowDownRight className="h-3.5 w-3.5" />
            {summary.missing} not seen
          </span>
          <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1 font-medium text-muted-foreground">
            <Minus className="h-3.5 w-3.5" />
            Net {summary.net > 0 ? "+" : ""}
            {summary.net}
          </span>
        </div>
      </div>
      {summary.baselineSources > 0 && (
        <p className="text-xs text-muted-foreground">
          {summary.baselineSources} source{summary.baselineSources === 1 ? "" : "s"} recorded an
          initial baseline; baseline collections are not growth.
        </p>
      )}
      {changedCompanies.length > 0 && (
        <details className="group border-t pt-2">
          <summary className="cursor-pointer text-xs font-medium text-primary">
            View company breakdown ({changedCompanies.length})
          </summary>
          <ul className="mt-2 divide-y">
            {changedCompanies.map((company) => (
              <li
                key={company.name}
                className="flex flex-wrap items-center justify-between gap-2 py-2"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{company.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {company.sourceCount} source{company.sourceCount === 1 ? "" : "s"}
                    {company.baselineSources > 0 && ` · ${company.baselineSources} baseline`}
                  </p>
                </div>
                <div className="flex flex-wrap gap-1.5 text-xs">
                  {company.added > 0 && <span className={addedStyle}>+{company.added}</span>}
                  {company.missing > 0 && (
                    <span className={missingStyle}>−{company.missing} not seen</span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </details>
      )}
    </section>
  );
}
