const APPROVED_LOGO_TYPES = new Set(["official_logo", "official_favicon", "careers_favicon"]);
const BLOCKED_BRANDING_HOSTS = new Set([
  "google.com",
  "www.google.com",
  "favicons.githubusercontent.com",
  "greenhouse.io",
  "lever.co",
  "teamtailor.com",
  "teamtailor-cdn.com",
]);

function isSafeEmployerBrandingUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    const host = parsed.hostname.toLowerCase();
    return (
      (parsed.protocol === "https:" || parsed.protocol === "http:") &&
      Boolean(parsed.hostname) &&
      !BLOCKED_BRANDING_HOSTS.has(host) &&
      !host.endsWith(".greenhouse.io") &&
      !host.endsWith(".lever.co") &&
      !host.endsWith(".teamtailor.com") &&
      !host.endsWith(".teamtailor-cdn.com")
    );
  } catch {
    return false;
  }
}

function normalizedHost(value: string): string {
  return new URL(value).hostname.toLowerCase().replace(/^www\./, "");
}

export function isApprovedEmployerBranding(
  value?: string | null,
  logoType?: string | null,
  sourceUrl?: string | null,
  websiteUrl?: string | null,
): boolean {
  if (!value || !logoType) return false;
  if (logoType !== "unverified" && !APPROVED_LOGO_TYPES.has(logoType)) {
    return false;
  }
  if (!isSafeEmployerBrandingUrl(value)) return false;
  if (sourceUrl && !isSafeEmployerBrandingUrl(sourceUrl)) return false;
  if (logoType !== "unverified") return true;
  if (!sourceUrl || !isSafeEmployerBrandingUrl(sourceUrl)) return false;
  if (websiteUrl && isSafeEmployerBrandingUrl(websiteUrl)) {
    const sourceHost = normalizedHost(sourceUrl);
    const websiteHost = normalizedHost(websiteUrl);
    if (sourceHost !== websiteHost && !sourceHost.endsWith(`.${websiteHost}`)) return false;
  }
  const sourcePath = new URL(sourceUrl).pathname.toLowerCase();
  return !/(^|\/)(careers?|jobs?|recruit(?:ment|ing)?)(\/|$)/.test(sourcePath);
}
