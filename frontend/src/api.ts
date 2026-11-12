export * from "./shared-contracts/employer-contracts";
export * from "./shared-contracts/vacancy-contracts";
export * from "./shared-contracts/discovery-contracts";
export * from "./shared-contracts/adapter-contracts";
export * from "./api-services/scout-http-client";

import { employerApiClient } from "./api-services/employer-api-client";
import { employerSourceApiClient } from "./api-services/employer-source-api-client";
import { vacancyApiClient } from "./api-services/vacancy-api-client";
import { extractionApiClient } from "./api-services/extraction-api-client";
import { discoveryApiClient } from "./api-services/discovery-api-client";

export const scoutApi = {
  ...employerApiClient,
  ...employerSourceApiClient,
  ...vacancyApiClient,
  ...extractionApiClient,
  ...discoveryApiClient,
};
