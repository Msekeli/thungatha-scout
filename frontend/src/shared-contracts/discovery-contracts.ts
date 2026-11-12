import type { SupportedAdapter } from "./adapter-contracts";

export type InspectionJob = {
  id: string | number;
  title: string;
  absolute_url?: string | null;
  location?: { name?: string | null };
  content?: string | null;
};

export type SourceInspection = {
  outcome: string;
  board_token: string;
  board_name: string | null;
  jobs: InspectionJob[];
  pages_fetched: number;
  complete: boolean;
  detail: string | null;
  source_url: string;
  board_url?: string;
  detected_adapter: SupportedAdapter;
  adapter_config: Record<string, string>;
  total_vacancies?: number | null;
};

export type GreenhouseInspection = SourceInspection;

export type CareersDiscovery = {
  careers_url: string;
  board_url: string;
  board_token: string;
  board_name: string | null;
  detected_adapter: SupportedAdapter;
  adapter_config: Record<string, string>;
  company_name: string;
  outcome?: string;
  jobs?: InspectionJob[];
  pages_fetched?: number;
  complete?: boolean;
  detail?: string | null;
  total_vacancies?: number | null;
};
