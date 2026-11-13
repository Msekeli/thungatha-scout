export type OrganizationType =
  | "direct_employer"
  | "recruitment_agency"
  | "staffing_company"
  | "hybrid"
  | "other"
  | "unresolved";

export type Employer = {
  id: string;
  name: string;
  legal_name?: string | null;
  website_url?: string | null;
  organization_type: OrganizationType | string;
  city?: string | null;
  province?: string | null;
  country?: string | null;
  logo_url?: string | null;
  logo_source_url?: string | null;
  logo_type?: "official_logo" | "official_favicon" | "careers_favicon" | "unverified";
  created_at?: string;
  vacancy_count?: number;
};

export type SourceDiscoveryPreview = {
  total_vacancies: number;
  crawl_complete?: boolean;
  pages_observed?: number;
  vacancies_found?: number;
  failed_urls?: string[];
  skipped_urls?: string[];
  pages?: {
    requested_url: string;
    final_url: string;
    status_code: number;
    content_type: string | null;
    page_title: string | null;
    platform_key: string | null;
    outcome: string;
    discovered_links: string[];
    vacancies_found: number;
    observed_at: string;
  }[];
  jobs: {
    id: string | number;
    title: string;
    absolute_url?: string | null;
    location?: { name?: string | null };
  }[];
};

export type EmployerSource = {
  id: string;
  employer_id: string;
  adapter_key: SupportedAdapter;
  source_url: string;
  employer_careers_url?: string | null;
  normalized_url: string;
  discovery_preview?: SourceDiscoveryPreview | null;
};
import type { SupportedAdapter } from "./adapter-contracts";
