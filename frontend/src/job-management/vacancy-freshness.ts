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

export function getVacancyFreshness(
  sourceUpdatedAt?: string | null,
  publishedAt?: string | null,
  now = Date.now(),
): VacancyFreshness | null {
  const updatedAt = parseTimestamp(sourceUpdatedAt);
  const effectiveDate = updatedAt ?? parseTimestamp(publishedAt);
  if (!effectiveDate) return null;

  const ageInDays = Math.max(
    0,
    Math.floor((now - effectiveDate.getTime()) / 86_400_000),
  );
  const sourceLabel = updatedAt ? "Updated" : "Posted";
  const dateLabel = effectiveDate.toLocaleDateString();
  const tone: VacancyFreshnessTone =
    ageInDays <= 7
      ? "fresh"
      : ageInDays <= 14
        ? "recent"
        : ageInDays <= 30
          ? "aging"
          : "stale";
  const statusLabel =
    tone === "fresh"
      ? "Fresh"
      : tone === "recent"
        ? "Recent"
        : tone === "aging"
          ? "Aging"
          : "Stale";

  return {
    label: `${sourceLabel} ${dateLabel} · ${ageInDays} ${ageInDays === 1 ? "day" : "days"} ago`,
    tone,
    statusLabel,
  };
}
