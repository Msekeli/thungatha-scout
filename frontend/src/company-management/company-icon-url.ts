const APPROVED_LOGO_TYPES = new Set(["official_logo", "official_favicon", "careers_favicon"]);

export function isApprovedEmployerBranding(
  value?: string | null,
  logoType?: string | null,
): boolean {
  if (!value || !logoType || !APPROVED_LOGO_TYPES.has(logoType)) return false;
  try {
    const parsed = new URL(value);
    return (
      (parsed.protocol === "https:" || parsed.protocol === "http:") && Boolean(parsed.hostname)
    );
  } catch {
    return false;
  }
}
