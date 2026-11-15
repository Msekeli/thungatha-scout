import { useState } from "react";
import { scoutApi } from "./api";
import type { Employer, EmployerSource, ExtractionRun } from "./api";

export type VacancyRunSummary = {
  added: number;
  missing: number;
  net: number;
  baselineCount: number;
  companies: { name: string; added: number; missing: number; baseline: boolean }[];
};

type Options = {
  dashboardSources: EmployerSource[];
  employers: Employer[];
  setExtracting: (value: boolean) => void;
  loadWorkspace: () => Promise<void>;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export function useVacancyFetching({
  dashboardSources,
  employers,
  setExtracting,
  loadWorkspace,
  onError,
  onNotice,
}: Options) {
  const [runSummary, setRunSummary] = useState<VacancyRunSummary | null>(null);

  async function fetchJobs() {
    if (!dashboardSources.length) {
      onError("No job sources are registered. Add an official careers URL first.");
      return;
    }
    setExtracting(true);
    setRunSummary(null);
    onError("");
    onNotice("");
    try {
      const results = await Promise.allSettled(
        dashboardSources.map((source) => scoutApi.extractSource(source.id)),
      );
      const completed = results
        .flatMap((result, index) =>
          result.status === "fulfilled"
            ? [
                {
                  run: result.value as ExtractionRun,
                  source: dashboardSources[index],
                },
              ]
            : [],
        )
        .filter(({ run }) => run.complete && ["success", "empty"].includes(run.outcome));
      const added = completed.reduce((sum, item) => sum + (item.run.jobs_added ?? 0), 0);
      const missing = completed.reduce((sum, item) => sum + (item.run.jobs_missing ?? 0), 0);
      const baselineCount = completed.filter((item) => item.run.is_baseline).length;
      const companies = new Map<
        string,
        { name: string; added: number; missing: number; baseline: boolean }
      >();
      completed.forEach(({ run, source }) => {
        const employer = employers.find((item) => item.id === source.employer_id);
        const name = employer?.name ?? "Unknown company";
        const entry = companies.get(source.employer_id) ?? {
          name,
          added: 0,
          missing: 0,
          baseline: false,
        };
        entry.baseline ||= Boolean(run.is_baseline);
        entry.added += run.jobs_added ?? 0;
        entry.missing += run.jobs_missing ?? 0;
        companies.set(source.employer_id, entry);
      });
      if (completed.length) {
        setRunSummary({
          added,
          missing,
          net: added - missing,
          baselineCount,
          companies: Array.from(companies.values()),
        });
        } else {
        setRunSummary(null);
      }
      await loadWorkspace();
      const failed = results.length - completed.length;
      onNotice(
        failed
          ? `Fetch finished: ${completed.length} source(s) returned; ${failed} failed.`
          : `Fetch finished: +${added} added, −${missing} missing, net ${added - missing}. Initial collections: ${baselineCount}.`,
      );
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not fetch jobs.");
    } finally {
      setExtracting(false);
    }
  }
  return { fetchJobs, runSummary };
}
