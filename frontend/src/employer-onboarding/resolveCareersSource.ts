import type { CareersDiscovery } from "../api";

function displayName(value: string): string {
  return value.replace(/[-_.]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function resolveCareersSource(url: string, name: string): CareersDiscovery | null {
  let parsed: URL;
  try {
    parsed = new URL(url.trim());
  } catch {
    return null;
  }
  if (parsed.protocol !== "https:") return null;
  const host = parsed.hostname.toLowerCase();
  const parts = parsed.pathname.split("/").filter(Boolean);
  let adapter: CareersDiscovery["detected_adapter"];
  let slug = "";
  let boardUrl = parsed.origin + parsed.pathname.replace(/\/$/, "");

  if (["boards.greenhouse.io", "job-boards.greenhouse.io"].includes(host)) {
    adapter = "greenhouse";
    slug = parts[0] ?? "";
    boardUrl = parsed.origin + "/" + slug;
  } else if (["jobs.lever.co", "jobs.eu.lever.co"].includes(host)) {
    adapter = "lever";
    slug = parts[0] ?? "";
    boardUrl = parsed.origin + "/" + slug;
  } else if (host.endsWith(".teamtailor.com")) {
    adapter = "teamtailor";
    slug = host.replace(/\.teamtailor\.com$/, "");
    boardUrl = parsed.origin + "/jobs";
  } else if (host === "apply.workable.com") {
    adapter = "workable";
    slug = parts[0] ?? "";
    boardUrl = parsed.origin + "/" + slug;
  } else {
    return null;
  }

  if (!slug || (adapter === "workable" && parts.length !== 1)) return null;
  const config =
    adapter === "greenhouse" || adapter === "workable"
      ? { slug }
      : adapter === "lever"
        ? { slug, region: host === "jobs.eu.lever.co" ? "eu" : "global" }
        : { careers_url: boardUrl };
  const companyName = name.trim() || displayName(slug);
  return {
    careers_url: url.trim(),
    board_url: boardUrl,
    board_token: slug,
    board_name: companyName,
    detected_adapter: adapter,
    adapter_config: config,
    company_name: companyName,
  };
}
