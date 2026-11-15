import type { Employer, EmployerSource, ExtractionRun } from "../api";

export type LatestRunSummary = {
  added: number;
  missing: number;
  net: number;
  baselineCount: number;
  companies: { name: string; added: number; missing: number; baseline: boolean }[];
};

export function getLatestExtractionRunSummary(
  sources: EmployerSource[],
  runsBySource: Record<string, ExtractionRun[]>,
  employers: Employer[],
): LatestRunSummary | null {
  const latest = sources.flatMap((source) => {
    const run = runsBySource[source.id]?.[0];
    return run?.complete && ["success", "empty"].includes(run.outcome) ? [{ source, run }] : [];
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
      baseline: false,
    };
    item.added += run.jobs_added ?? 0;
    item.missing += run.jobs_missing ?? 0;
    item.baseline ||= Boolean(run.is_baseline);
    companies.set(source.employer_id, item);
  });
  const added = latest.reduce((sum, item) => sum + (item.run.jobs_added ?? 0), 0);
  const missing = latest.reduce((sum, item) => sum + (item.run.jobs_missing ?? 0), 0);
  return {
    added,
    missing,
    net: added - missing,
    baselineCount: latest.filter((item) => item.run.is_baseline).length,
    companies: Array.from(companies.values()),
  };
}
