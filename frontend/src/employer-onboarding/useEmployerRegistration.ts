import type { FormEvent } from "react";
import { scoutApi } from "../api";
import { getCompanyIconUrl } from "../company-management/company-icon-url";
import { runEmployerVacancyImport } from "./runEmployerVacancyImport";
import { findEmployerDuplicate } from "./findEmployerDuplicate";
import type { CareersDiscovery, Employer, EmployerSource } from "../api";

type EmployerRegistrationForm = {
  name: string;
  website_url: string;
  organization_type: string;
};
type UseEmployerRegistrationOptions = {
  form: EmployerRegistrationForm;
  sourceUrl: string;
  employers: Employer[];
  sources: EmployerSource[];
  loadWorkspace: () => Promise<void>;
  setSaving: (value: boolean) => void;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
  onRegistered: (result: { employer: Employer; source: EmployerSource }) => void;
};

export function useEmployerRegistration(options: UseEmployerRegistrationOptions) {
  const {
    form,
    sourceUrl,
    employers,
    sources,
    loadWorkspace,
    setSaving,
    onError,
    onNotice,
    onRegistered,
  } = options;

  async function register(event: FormEvent<HTMLFormElement>, discovery: CareersDiscovery) {
    event.preventDefault();
    const companyName = form.name.trim() || discovery.company_name;
    if (!companyName) {
      onError("Enter the employer name before registering this recruitment source.");
      return;
    }
    if (
      ["lever", "teamtailor"].includes(discovery.detected_adapter) &&
      ((discovery.outcome !== "success" && discovery.outcome !== "empty") ||
        discovery.complete !== true)
    ) {
      onError(discovery.detail || "The ATS board could not be inspected completely.");
      return;
    }

    const duplicate = findEmployerDuplicate(sourceUrl, companyName, employers, sources);
    if (duplicate?.kind === "source") {
      onError(
        "This recruitment source is already registered under " + duplicate.employer.name + ".",
      );
      return;
    }

    setSaving(true);
    onError("");
    onNotice("");
    let employer: Employer | null = null;
    try {
      employer =
        duplicate?.kind === "employer"
          ? duplicate.employer
          : await scoutApi.createEmployer({
              ...form,
              name: companyName,
              website_url: form.website_url.trim() || null,
              logo_url: getCompanyIconUrl(form.website_url.trim() || null),
              logo_source_url: form.website_url.trim() || null,
            });

      const source = await scoutApi.createSource(employer.id, {
        adapter_key: discovery.detected_adapter,
        source_url: discovery.board_url,
        normalized_url: discovery.board_url,
        employer_careers_url: sourceUrl,
        adapter_config: discovery.adapter_config,
        discovery_preview:
          discovery.complete === true &&
          (discovery.outcome === "success" || discovery.outcome === "empty")
            ? {
                total_vacancies: discovery.total_vacancies ?? discovery.jobs?.length ?? 0,
                jobs: discovery.jobs ?? [],
              }
            : null,
      });
      onRegistered({ employer, source });
      const previewCount = source.discovery_preview?.total_vacancies;
      onNotice(
        previewCount === undefined
          ? employer.name + " added. Vacancy preview is not available yet."
          : employer.name + " added. " + previewCount + " vacancies discovered.",
      );
      // Extraction runs in the background; registration must not wait for vacancy imports.
      void runEmployerVacancyImport(source.id, employer.name, {
        loadWorkspace,
        onError,
        onNotice,
      });
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : "An unexpected error occurred.";
      onError(
        employer
          ? employer.name + " was added, but source registration needs attention: " + detail
          : "Could not add the company: " + detail,
      );
      if (employer) void loadWorkspace().catch(() => undefined);
    } finally {
      setSaving(false);
    }
  }
  return { register };
}
