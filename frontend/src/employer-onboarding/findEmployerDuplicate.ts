import type { Employer, EmployerSource } from "../api";

export type EmployerDuplicateMatch =
  | { kind: "source"; employer: Employer; source: EmployerSource }
  | { kind: "employer"; employer: Employer };

export function normalizeCareersUrl(value: string): string {
  try {
    const url = new URL(value.trim());
    url.hash = "";
    url.search = "";
    url.hostname = url.hostname.toLowerCase().replace(/^www\./, "");
    url.pathname = url.pathname.replace(/\/+$/, "") || "/";
    return url.toString().replace(/\/$/, "");
  } catch {
    return value.trim().toLowerCase().replace(/\/+$/, "");
  }
}

export function normalizeEmployerName(value: string): string {
  return value.toLocaleLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

export function findEmployerDuplicate(
  sourceUrl: string,
  companyName: string,
  employers: Employer[],
  sources: EmployerSource[],
): EmployerDuplicateMatch | null {
  const candidateUrl = normalizeCareersUrl(sourceUrl);
  if (candidateUrl) {
    const matchingSource = sources.find((source) =>
      [source.source_url, source.normalized_url, source.employer_careers_url]
        .filter((value): value is string => Boolean(value))
        .some((value) => normalizeCareersUrl(value) === candidateUrl),
    );
    if (matchingSource) {
      const employer = employers.find((item) => item.id === matchingSource.employer_id);
      if (employer) return { kind: "source", employer, source: matchingSource };
    }
  }

  const candidateName = normalizeEmployerName(companyName);
  if (candidateName) {
    const employer = employers.find((item) => normalizeEmployerName(item.name) === candidateName);
    if (employer) return { kind: "employer", employer };
  }
  return null;
}
