import { strict as assert } from "node:assert";
import { resolveCareersSource } from "./resolveCareersSource.ts";
import { ADAPTER_LABELS, SUPPORTED_ADAPTERS } from "../shared-contracts/adapter-contracts.ts";

const source = resolveCareersSource(
  "https://apply.workable.com/lekkeslaap/",
  "LekkeSlaap",
);

assert.deepEqual(source, {
  careers_url: "https://apply.workable.com/lekkeslaap/",
  board_url: "https://apply.workable.com/lekkeslaap",
  board_token: "lekkeslaap",
  board_name: "LekkeSlaap",
  detected_adapter: "workable",
  adapter_config: { slug: "lekkeslaap" },
  company_name: "LekkeSlaap",
});
assert.ok(SUPPORTED_ADAPTERS.includes("workable"));
assert.deepEqual(ADAPTER_LABELS.workable, { label: "Workable", badge: "W" });
