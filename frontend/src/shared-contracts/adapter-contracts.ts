export const SUPPORTED_ADAPTERS = [
  "career_page",
  "greenhouse",
  "lever",
  "teamtailor",
  "workable",
  "workday",
] as const;

export type SupportedAdapter = (typeof SUPPORTED_ADAPTERS)[number];

export const ADAPTER_LABELS: Record<SupportedAdapter, { label: string; badge: string }> = {
  career_page: { label: "Career page", badge: "C" },
  greenhouse: { label: "Greenhouse", badge: "G" },
  lever: { label: "Lever", badge: "L" },
  teamtailor: { label: "Teamtailor", badge: "T" },
  workable: { label: "Workable", badge: "W" },
  workday: { label: "Workday", badge: "W" },
};
