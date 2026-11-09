export function getCompanyIconUrl(sourceUrl?: string | null): string | null {
  if (!sourceUrl) return null;
  try {
    const parsed = new URL(sourceUrl);
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
    return (
      "https://www.google.com/s2/favicons?domain=" + encodeURIComponent(parsed.hostname) + "&sz=128"
    );
  } catch {
    return null;
  }
}
