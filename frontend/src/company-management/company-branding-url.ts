export function isGoogleFaviconHost(value: string): boolean {
  try {
    return ["google.com", "www.google.com"].includes(new URL(value).hostname.toLowerCase());
  } catch {
    return false;
  }
}

const BLOCKED_BRANDING_HOSTS = new Set([
  "google.com",
  "www.google.com",
  "favicons.githubusercontent.com",
  "greenhouse.io",
  "lever.co",
  "teamtailor.com",
  "teamtailor-cdn.com",
  "myworkdayjobs.com",
  "workable.com",
]);

function normalizeHost(host: string): string {
  return host
    .toLowerCase()
    .replace(/^www\./, "")
    .replace(/\.$/, "");
}

function isTrustedAtsBrandingAsset(url: URL): boolean {
  const host = url.hostname.toLowerCase();
  const path = url.pathname;
  return (
    (host.endsWith(".myworkdayjobs.com") && path.endsWith("/assets/logo")) ||
    (host === "recruiting.cdn.greenhouse.io" &&
      path.includes("/external_greenhouse_job_boards/logos/")) ||
    (host === "images.teamtailor-cdn.com" && path.includes("/logotype-v3/"))
  );
}

function isBlockedBrandingHost(host: string): boolean {
  const normalized = host.toLowerCase().replace(/\.$/, "");
  return (
    BLOCKED_BRANDING_HOSTS.has(normalized) ||
    normalized.endsWith(".greenhouse.io") ||
    normalized.endsWith(".lever.co") ||
    normalized.endsWith(".teamtailor.com") ||
    normalized.endsWith(".teamtailor-cdn.com") ||
    normalized.endsWith(".myworkdayjobs.com") ||
    normalized.endsWith(".workable.com")
  );
}

export function parseSafeBrandingUrl(value: string): URL | null {
  try {
    const parsed = new URL(value);
    if (
      (parsed.protocol !== "https:" && parsed.protocol !== "http:") ||
      !parsed.hostname ||
      parsed.username ||
      parsed.password ||
      (isBlockedBrandingHost(parsed.hostname) && !isTrustedAtsBrandingAsset(parsed))
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function isSafeBrandingSourceUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return (
      ["https:", "http:"].includes(url.protocol) && !!url.hostname && !url.username && !url.password
    );
  } catch {
    return false;
  }
}

export function isGoogleFaviconForWebsite(value: string, websiteUrl?: string | null): boolean {
  if (!websiteUrl) return false;
  try {
    const favicon = new URL(value);
    const website = new URL(websiteUrl);
    if (
      favicon.protocol !== "https:" ||
      !["google.com", "www.google.com"].includes(favicon.hostname.toLowerCase()) ||
      favicon.pathname !== "/s2/favicons"
    ) {
      return false;
    }
    const requestedDomain = favicon.searchParams.get("domain");
    return Boolean(
      requestedDomain && normalizeHost(requestedDomain) === normalizeHost(website.hostname),
    );
  } catch {
    return false;
  }
}
