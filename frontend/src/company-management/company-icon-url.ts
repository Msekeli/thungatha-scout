const BLOCKED_LOGO_HOSTS = new Set([
  "boards.greenhouse.io",
  "job-boards.greenhouse.io",
  "job-boards.eu.greenhouse.io",
  "jobs.lever.co",
  "jobs.eu.lever.co",
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
      BLOCKED_LOGO_HOSTS.has(host) ||
      host.endsWith(".teamtailor.com")
    ) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}
