export function getCompanyIconUrl(websiteUrl?: string | null): string | null {
  if (!websiteUrl) return null;
  try {
    const parsed = new URL(websiteUrl);
    if (parsed.protocol !== "https:" && parsed.protocol !== "http:") return null;
    return (
      "https://www.google.com/s2/favicons?domain=" +
      encodeURIComponent(parsed.hostname) +
      "&sz=128"
    );
  } catch {
    return null;
  }
}
