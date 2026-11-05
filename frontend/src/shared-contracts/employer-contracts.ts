export type OrganizationType =
  | "direct_employer"
  | "recruitment_agency"
  | "staffing_company"
  | "hybrid"
  | "other"
  | "unresolved";

export type CompanyStatus =
  | "discovered"
  | "pending_review"
  | "approved"
  | "rejected"
  | "needs_review"
  | "inactive";

export type Employer = {
  id: string;
  name: string;
  legal_name?: string | null;
  website_url?: string | null;
  organization_type: OrganizationType | string;
  status: CompanyStatus | string;
  city?: string | null;
  province?: string | null;
  country?: string | null;
  logo_url?: string | null;
  logo_source_url?: string | null;
  created_at?: string;
};

export type RelationshipEvidence = {
  evidence_url?: string | null;
  decision_reason?: string | null;
  recorded_at?: string | null;
};

export type EmployerSource = {
  id: string;
  employer_id: string;
  adapter_key: "greenhouse" | "workday";
  source_url: string;
  employer_careers_url?: string | null;
  normalized_url: string;
  status: string;
  permission_status: string;
  relationship_evidence?: RelationshipEvidence[];
};
