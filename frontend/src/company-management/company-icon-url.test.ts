import { strict as assert } from "node:assert";
import { isApprovedEmployerBranding } from "./company-icon-url.ts";

assert.equal(isApprovedEmployerBranding("https://cdn.example.com/logo.svg", "manual"), false);
assert.equal(isApprovedEmployerBranding("https://cdn.example.com/logo.svg", "official_logo"), true);
assert.equal(
  isApprovedEmployerBranding("https://jobs.lever.co/example/favicon.ico", "unverified"),
  false,
);
assert.equal(
  isApprovedEmployerBranding("https://www.google.com/s2/favicons?domain=example.com", "unverified"),
  false,
);
assert.equal(
  isApprovedEmployerBranding(
    "https://cdn.example.com/logo.svg",
    "unverified",
    "https://employer.example.com/",
  ),
  true,
);
assert.equal(
  isApprovedEmployerBranding(
    "https://cdn.example.com/logo.svg",
    "unverified",
    "https://employer.teamtailor.com/jobs",
  ),
  true,
);
assert.equal(
  isApprovedEmployerBranding(
    "https://cdn.example.com/logo.svg",
    "unverified",
    "https://employer.example.com/careers",
  ),
  true,
);
assert.equal(
  isApprovedEmployerBranding(
    "https://images.external-cdn.example/logo.svg",
    "unverified",
    "https://employer.example.com/",
  ),
  true,
);
assert.equal(
  isApprovedEmployerBranding("https://images.teamtailor-cdn.com/logo.svg", "official_logo"),
  false,
);
assert.equal(isApprovedEmployerBranding("https://cdn.example.com/logo.svg", "unverified"), true);
assert.equal(
  isApprovedEmployerBranding(
    "https://cdn.example.com/logo.svg",
    "unverified",
    "https://employer.example.com/about",
  ),
  true,
);

assert.equal(
  isApprovedEmployerBranding(
    "https://www.google.com/s2/favicons?domain=www.takealot.com&sz=128",
    "unverified",
    "https://www.takealot.com/",
    "https://www.takealot.com",
  ),
  true,
);
assert.equal(
  isApprovedEmployerBranding(
    "https://www.google.com/s2/favicons?domain=other.example&sz=128",
    "unverified",
    "https://www.takealot.com/",
    "https://www.takealot.com",
  ),
  false,
);

assert.equal(
  isApprovedEmployerBranding("https://apply.workable.com/logo.png", "official_logo"),
  false,
);
