const ATS_HOSTS = new Set([
  "boards.greenhouse.io",
  "job-boards.greenhouse.io",
  "jobs.lever.co",
  "jobs.eu.lever.co",
]);

export function getCompanyIconUrl(websiteUrl?: string | null): string | null {
  if (!websiteUrl) return null;
  try {
    const parsed = new URL(websiteUrl);
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
    if (
      ATS_HOSTS.has(parsed.hostname.toLowerCase()) ||
      parsed.hostname.endsWith(".teamtailor.com")
    ) {
      return null;
    }
    return (
      "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(parsed.hostname) + "&sz=128"
    );
  } catch {
    return null;
  }
}
