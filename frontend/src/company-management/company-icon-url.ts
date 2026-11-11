const APPROVED_LOGO_TYPES = new Set(["official_logo", "official_favicon", "careers_favicon"]);
const BLOCKED_BRANDING_HOSTS = new Set([
  "google.com",
  "www.google.com",
  "favicons.githubusercontent.com",
  "greenhouse.io",
  "lever.co",
  "teamtailor.com",
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
      !host.endsWith(".teamtailor.com")
    );
  } catch {
    return false;
  }
}

export function isApprovedEmployerBranding(
  value?: string | null,
  logoType?: string | null,
): boolean {
  if (!value) return false;
  if (logoType && logoType !== "unverified" && !APPROVED_LOGO_TYPES.has(logoType)) {
    return false;
  }
  return isSafeEmployerBrandingUrl(value);
}
