import { useEffect, useRef, useState } from "react";
import type { Vacancy } from "../api";

const STORAGE_KEY = "thungatha-scout-vacancy-count-snapshot";

export function useVacancyCountChange(page: string, vacancies: Vacancy[]) {
  const isJobsPage = page === "jobs";
  const currentCount = vacancies.length;
  const currentCountRef = useRef(currentCount);
  const [previousCount, setPreviousCount] = useState<number | null>(null);
  const wasOnJobsPage = useRef(false);

  currentCountRef.current = currentCount;

  useEffect(() => {
    if (isJobsPage && !wasOnJobsPage.current) {
      try {
        const saved = window.localStorage.getItem(STORAGE_KEY);
        setPreviousCount(saved === null ? null : Number(saved));
      } catch {
        setPreviousCount(null);
      }
    } else if (!isJobsPage && wasOnJobsPage.current) {
      try {
        window.localStorage.setItem(STORAGE_KEY, String(currentCountRef.current));
      } catch {
        // Keep the workspace usable when browser storage is unavailable.
      }
      setPreviousCount(null);
    }
    wasOnJobsPage.current = isJobsPage;
  }, [isJobsPage]);

  return previousCount === null ? 0 : currentCount - previousCount;
}
