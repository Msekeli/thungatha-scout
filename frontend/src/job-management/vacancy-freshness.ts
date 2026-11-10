export type VacancyFreshnessTone = "fresh" | "recent" | "aging" | "stale";

export type VacancyFreshness = {
  label: string;
  tone: VacancyFreshnessTone;
  statusLabel: string;
};

function parseTimestamp(value?: string | null): Date | null {
  if (!value) return null;
  const timestamp = new Date(value);
  return Number.isNaN(timestamp.getTime()) ? null : timestamp;
}

function getAgeLabel(ageInMilliseconds: number): string {
  if (ageInMilliseconds < 3_600_000) return "less than 1 hour ago";
  if (ageInMilliseconds < 86_400_000) {
    const hours = Math.floor(ageInMilliseconds / 3_600_000);
    return `${hours} ${hours === 1 ? "hour" : "hours"} ago`;
  }
  const days = Math.floor(ageInMilliseconds / 86_400_000);
  return `${days} ${days === 1 ? "day" : "days"} ago`;
}

export function getVacancyFreshness(
  sourceUpdatedAt?: string | null,
  publishedAt?: string | null,
  now = Date.now(),
): VacancyFreshness | null {
  const updatedAt = parseTimestamp(sourceUpdatedAt);
  const effectiveDate = updatedAt ?? parseTimestamp(publishedAt);
  if (!effectiveDate) return null;

  const ageInMilliseconds = Math.max(0, now - effectiveDate.getTime());
  const ageInDays = Math.floor(ageInMilliseconds / 86_400_000);
  const sourceLabel = updatedAt ? "Updated" : "Posted";
  const dateLabel = effectiveDate.toLocaleDateString();
  const tone: VacancyFreshnessTone =
    ageInDays <= 7 ? "fresh" : ageInDays <= 14 ? "recent" : ageInDays <= 30 ? "aging" : "stale";
  const statusLabel =
    tone === "fresh"
      ? "Fresh"
      : tone === "recent"
        ? "Recent"
        : tone === "aging"
          ? "Aging"
          : "Stale";

  return {
    label: `${sourceLabel} ${dateLabel} · ${getAgeLabel(ageInMilliseconds)}`,
    tone,
    statusLabel,
  };
}
