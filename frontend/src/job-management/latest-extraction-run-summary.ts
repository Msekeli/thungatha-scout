import type { Employer, EmployerSource, ExtractionRun } from "../api";

export type LatestRunSummary = {
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

export function getLatestExtractionRunSummary(
  sources: EmployerSource[],
  runsBySource: Record<string, ExtractionRun[]>,
  employers: Employer[],
): LatestRunSummary | null {
  const latest = sources.flatMap((source) => {
    const run = runsBySource[source.id]?.find(
      (item) => item.complete && ["success", "empty"].includes(item.outcome),
    );
    return run ? [{ source, run }] : [];
  });
  if (!latest.length) return null;

  const companies = new Map<string, LatestRunSummary["companies"][number]>();
  latest.forEach(({ source, run }) => {
    const name =
      employers.find((item) => item.id === source.employer_id)?.name ?? "Unknown company";
    const item = companies.get(source.employer_id) ?? {
      name,
      added: 0,
      missing: 0,
      baselineSources: 0,
      sourceCount: 0,
    };
    item.added += run.jobs_added ?? 0;
    item.missing += run.jobs_missing ?? 0;
    item.baselineSources += Number(Boolean(run.is_baseline));
    item.sourceCount += 1;
    companies.set(source.employer_id, item);
  });

  const added = latest.reduce((sum, item) => sum + (item.run.jobs_added ?? 0), 0);
  const missing = latest.reduce((sum, item) => sum + (item.run.jobs_missing ?? 0), 0);
  return {
    added,
    missing,
    net: added - missing,
    baselineSources: latest.filter((item) => item.run.is_baseline).length,
    sourceCount: latest.length,
    companies: Array.from(companies.values()).sort(
      (a, b) => b.added + b.missing - (a.added + a.missing) || a.name.localeCompare(b.name),
    ),
  };
}
