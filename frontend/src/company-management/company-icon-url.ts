const APPROVED_LOGO_TYPES = new Set(["official_logo", "official_favicon", "careers_favicon"]);
const BLOCKED_BRANDING_HOSTS = new Set([
  "google.com",
  "www.google.com",
  "favicons.githubusercontent.com",
  "greenhouse.io",
  "lever.co",
  "teamtailor.com",
  "teamtailor-cdn.com",
  "myworkdayjobs.com",
]);

function isBlockedBrandingHost(host: string): boolean {
  const normalized = host.toLowerCase().replace(/\\.$/, "");
  return (
    BLOCKED_BRANDING_HOSTS.has(normalized) ||
    normalized.endsWith(".greenhouse.io") ||
    normalized.endsWith(".lever.co") ||
    normalized.endsWith(".teamtailor.com") ||
    normalized.endsWith(".teamtailor-cdn.com") ||
    normalized.endsWith(".myworkdayjobs.com")
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

function isCareersOrJobsPath(value: string): boolean {
  const path = new URL(value).pathname.toLowerCase();
  return /(^|\\/)(careers?|jobs?|recruit(?:ment|ing)?)(\\/|$)/.test(path);
}

export function isApprovedEmployerBranding(
  value?: string | null,
  logoType?: string | null,
  sourceUrl?: string | null,
): boolean {
  if (!value || !logoType) return false;

  const logo = parseSafeBrandingUrl(value);
  if (!logo) return false;

  if (APPROVED_LOGO_TYPES.has(logoType)) {
    return !sourceUrl || parseSafeBrandingUrl(sourceUrl) !== null;
  }
  if (logoType !== "unverified") return false;

  // Legacy records predate provenance tracking. Keep their existing logo visible
  // unless we have positive evidence that it came from a careers/ATS page.
  if (!sourceUrl) return true;

  const source = parseSafeBrandingUrl(sourceUrl);
  return source !== null && !isCareersOrJobsPath(source.href);
}
