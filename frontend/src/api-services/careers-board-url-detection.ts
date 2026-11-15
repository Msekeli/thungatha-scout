export function isLeverBoardUrl(value: string): boolean {
  try {
    return ["jobs.lever.co", "jobs.eu.lever.co"].includes(new URL(value).hostname);
  } catch {
    return false;
  }
}

export function isWorkableBoardUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return (
      url.hostname === "apply.workable.com" && url.pathname.split("/").filter(Boolean).length === 1
    );
  } catch {
    return false;
  }
}

export function isWorkdayBoardUrl(value: string): boolean {
  try {
    const url = new URL(value);
    const parts = url.pathname.split("/").filter(Boolean);
    if (/^[a-z]{2}-[A-Z]{2}$/.test(parts[0] ?? "")) parts.shift();
    return (
      url.protocol === "https:" &&
      /^[a-z0-9-]+\.wd[0-9]+\.myworkdayjobs\.com$/.test(url.hostname) &&
      parts.length === 1
    );
  } catch {
    return false;
  }
}

export function isGreenhouseBoardUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return ["boards.greenhouse.io", "job-boards.greenhouse.io"].includes(url.hostname);
  } catch {
    return false;
  }
}

export function isTeamtailorBoardUrl(value: string): boolean {
  try {
    return new URL(value).hostname.endsWith(".teamtailor.com");
  } catch {
    return false;
  }
}
