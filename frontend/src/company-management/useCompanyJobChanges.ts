import { useEffect, useMemo, useRef, useState } from "react";
import type { Employer, Vacancy } from "../api";

const STORAGE_KEY = "thungatha-scout-company-job-snapshot";
type Snapshot = Record<string, number>;

export function useCompanyJobChanges(
  page: string,
  employers: Employer[],
  vacancies: Vacancy[],
) {
  const inCompanyArea = page !== "jobs";
  const currentCounts = useMemo(
    () =>
      employers.reduce<Snapshot>((counts, employer) => {
        counts[employer.id] = vacancies.filter(
          (vacancy) => vacancy.employer_id === employer.id,
        ).length;
        return counts;
      }, {}),
    [employers, vacancies],
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
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(currentCountsRef.current),
      );
      setPreviousCounts(null);
    }
    wasInCompanyArea.current = inCompanyArea;
  }, [inCompanyArea]);

  return useMemo(() => {
    if (!previousCounts) return {};
    return Object.fromEntries(
      Object.entries(currentCounts)
        .map(([id, count]) => [id, count - (previousCounts[id] ?? count)])
        .filter(([, change]) => change !== 0),
    ) as Snapshot;
  }, [currentCounts, previousCounts]);
}
