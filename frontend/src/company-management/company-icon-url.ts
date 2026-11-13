import {
  isGoogleFaviconForWebsite,
  isSafeBrandingSourceUrl,
  parseSafeBrandingUrl,
} from "./company-branding-url.ts";

const APPROVED_LOGO_TYPES = new Set(["official_logo", "official_favicon", "careers_favicon"]);

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
