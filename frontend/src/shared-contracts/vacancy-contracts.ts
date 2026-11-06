export type VacancyLocationScope = "cape_town" | "western_cape" | "south_africa" | "all";

export type VacancyPage = {
  items: Vacancy[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
};

export type Vacancy = {
  id: string;
  employer_id: string;
  employer_name: string;
  source_id: string;
  external_job_id: string;
  title: string;
  description?: string | null;
  location_text?: string | null;
  department?: string | null;
  office?: string | null;
  source_url: string;
  application_url: string;
  source_updated_at?: string | null;
  first_seen_at?: string;
  last_seen_at: string;
  archived_at?: string | null;
  archived_reason?: string | null;
  employer_logo_url?: string | null;
  employer_logo_source_url?: string | null;
};

export type ExtractionRun = {
  id: string;
  source_id: string;
  outcome: string;
  jobs_received: number;
  jobs_inserted: number;
  jobs_updated: number;
  complete: boolean;
  detail?: string | null;
  started_at?: string;
  finished_at?: string | null;
};
