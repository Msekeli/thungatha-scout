export type VacancyFreshnessTone = "fresh" | "recent" | "aging" | "stale";

export type VacancyFreshness = { dateLabel: string; ageLabel: string; tone: VacancyFreshnessTone };

function parseTimestamp(value?: string | null): Date | null {
  if (!value) return null;
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? null : timestamp;
}

function getAgeLabel(age: number): string {
  if (age < 3_600_000) return "less than 1 hour ago";
  if (age < 86_400_000) {
    const hours = Math.floor(age / 3_600_000);
    return hours + " " + (hours === 1 ? "hour" : "hours") + " ago";
  }
  const days = Math.floor(age / 86_400_000);
  return days + " " + (days === 1 ? "day" : "days") + " ago";
}

export function getVacancyFreshness(sourceUpdatedAt?: string | null, publishedAt?: string | null, now = Date.now()): VacancyFreshness | null {
  const updatedAt = parseTimestamp(sourceUpdatedAt);
  const effectiveDate = updatedAt ?? parseTimestamp(publishedAt);
  if (!effectiveDate) return null;
  const age = Math.max(0, now - effectiveDate.getTime());
  const days = Math.floor(age / 86_400_000);
  const tone: VacancyFreshnessTone = days <= 7 ? "fresh" : days <= 14 ? "recent" : days <= 30 ? "aging" : "stale";
  return {
    dateLabel: (updatedAt ? "Updated " : "Posted ") + effectiveDate.toLocaleDateString(),
    ageLabel: getAgeLabel(age),
    tone,
  };
}
