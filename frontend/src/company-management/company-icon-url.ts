const BLOCKED_LOGO_HOSTS = new Set([
  "boards.greenhouse.io",
  "job-boards.greenhouse.io",
  "job-boards.eu.greenhouse.io",
  "jobs.lever.co",
  "jobs.eu.lever.co",
  "teamtailor.com",
]);

export function isEmployerLogoUrl(value?: string | null): boolean {
  if (!value) return false;
  try {
    const parsed = new URL(value);
    const host = parsed.hostname.toLowerCase();
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return false;
    if (
      host === "www.google.com" ||
      host === "google.com" ||
      host === "favicons.githubusercontent.com" ||
      BLOCKED_LOGO_HOSTS.has(host)
    ) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

export function getCompanyFaviconUrl(websiteUrl?: string | null): string | null {
  if (!websiteUrl) return null;
  try {
    const parsed = new URL(websiteUrl);
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
    const host = parsed.hostname.toLowerCase();
    // The favicon belongs to the exact website shown in the browser tab.
    // ATS-hosted career sites are valid favicon sources for this UI fallback.
    return "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(host) + "&sz=128";
  } catch {
    return null;
  }
}
