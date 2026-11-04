export type InspectionJob = {
  id: number;
  title: string;
  absolute_url: string;
  location?: { name?: string };
  content?: string;
};

export type GreenhouseInspection = {
  outcome: string;
  board_token: string;
  board_name: string | null;
  jobs: InspectionJob[];
  pages_fetched: number;
  complete: boolean;
  detail: string | null;
  source_url: string;
};

export type CareersDiscovery = GreenhouseInspection & {
  careers_url: string;
  board_url: string;
  detected_adapter: "greenhouse";
  company_name?: string;
};
