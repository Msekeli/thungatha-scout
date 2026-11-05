import { useEffect, useMemo, useRef, useState } from "react";
import type { Employer, Vacancy } from "../api";

const STORAGE_KEY = "thungatha-scout-company-job-snapshot";
type Snapshot = Record<string, number>;

export function useCompanyJobChanges(page: string, employers: Employer[], _vacancies: Vacancy[]) {
  const inCompanyArea = page !== "jobs";
  const currentCounts = useMemo(
    () =>
      employers.reduce<Snapshot>((counts, employer) => {
        counts[employer.id] = employer.vacancy_count ?? 0;
        return counts;
      }, {}),
    [employers],
  );
  const currentCountsRef = useRef(currentCounts);
  const [previousCounts, setPreviousCounts] = useState<Snapshot | null>(null);
  const wasInCompanyArea = useRef(false);

  currentCountsRef.current = currentCounts;

  useEffect(() => {
    if (inCompanyArea && !wasInCompanyArea.current) {
      try {
        const saved = window.localStorage.getItem(STORAGE_KEY);
        setPreviousCounts(saved ? (JSON.parse(saved) as Snapshot) : {});
      } catch {
        setPreviousCounts({});
      }
    } else if (!inCompanyArea && wasInCompanyArea.current) {
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(currentCountsRef.current));
      } catch {
        // Keep the directory usable when browser storage is unavailable.
      }
      setPreviousCounts(null);
    }
    wasInCompanyArea.current = inCompanyArea;
  }, [inCompanyArea]);

  const changes = useMemo(() => {
    if (!previousCounts) return {};
    return Object.fromEntries(
      Object.entries(currentCounts)
        .map(([id, count]) => [id, count - (previousCounts[id] ?? count)])
        .filter(([, change]) => change !== 0),
    ) as Snapshot;
  }, [currentCounts, previousCounts]);

  return { currentJobsByEmployer: currentCounts, jobChangesByEmployer: changes };
}
