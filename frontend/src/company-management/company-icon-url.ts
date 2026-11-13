const APPROVED_LOGO_TYPES = new Set(["official_logo", "official_favicon", "careers_favicon"]);
const BLOCKED_BRANDING_HOSTS = new Set([
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

function parseSafeBrandingUrl(value: string): URL | null {
  try {
    const parsed = new URL(value);
    if (
      (parsed.protocol !== "https:" && parsed.protocol !== "http:") ||
      !parsed.hostname ||
      parsed.username ||
      parsed.password ||
      isBlockedBrandingHost(parsed.hostname)
    ) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

function isSafeBrandingSourceUrl(value: string): boolean {
  try { const url = new URL(value); return ["https:", "http:"].includes(url.protocol) && !!url.hostname && !url.username && !url.password; }
  catch { return false; }
}

function isGoogleFaviconForWebsite(value: string, websiteUrl?: string | null): boolean {
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

export function isApprovedEmployerBranding(
  value?: string | null,
  logoType?: string | null,
  sourceUrl?: string | null,
  websiteUrl?: string | null,
): boolean {
  if (!value || !logoType) return false;

  // Google's favicon endpoint is a valid domain-specific fallback only when its
  // requested domain matches this employer's configured website.
  const googleFavicon = isGoogleFaviconForWebsite(value, websiteUrl);
  const logo = googleFavicon ? null : parseSafeBrandingUrl(value);
  if (!googleFavicon && !logo) return false;

  if (APPROVED_LOGO_TYPES.has(logoType)) {
    return !sourceUrl || isSafeBrandingSourceUrl(sourceUrl);
  }
  if (logoType !== "unverified") return false;

  // Legacy logos remain visible. A careers-page path alone does not prove that
  // the asset belongs to an ATS; block only known ATS/unsafe hosts.
  if (!sourceUrl) return true;
  return isSafeBrandingSourceUrl(sourceUrl);
}
