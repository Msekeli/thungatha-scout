import { strict as assert } from "node:assert";
import { isApprovedEmployerBranding } from "./company-icon-url.ts";

assert.equal(
  isApprovedEmployerBranding("https://cdn.example.com/logo.svg", "manual"),
  false,
);
assert.equal(
  isApprovedEmployerBranding("https://cdn.example.com/logo.svg", "official_logo"),
  true,
);
assert.equal(
  isApprovedEmployerBranding("https://jobs.lever.co/example/favicon.ico", "unverified"),
  false,
);
assert.equal(
  isApprovedEmployerBranding(
    "https://www.google.com/s2/favicons?domain=example.com",
    "unverified",
  ),
  false,
);
assert.equal(
  isApprovedEmployerBranding("https://cdn.example.com/logo.svg", "unverified"),
  true,
);
