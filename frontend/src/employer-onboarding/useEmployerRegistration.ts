import type { FormEvent } from "react";
import { scoutApi } from "../api";
import { getCompanyIconUrl } from "../company-management/company-icon-url";
import type { CareersDiscovery, Employer, EmployerSource } from "../api";

type EmployerRegistrationForm = {
  name: string;
  website_url: string;
  organization_type: string;
};

type UseEmployerRegistrationOptions = {
  form: EmployerRegistrationForm;
  sourceUrl: string;
  loadWorkspace: () => Promise<void>;
  setSaving: (value: boolean) => void;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
  onRegistered: (result: { employer: Employer; source: EmployerSource }) => void;
};

export function useEmployerRegistration(options: UseEmployerRegistrationOptions) {
  const { form, sourceUrl, loadWorkspace, setSaving, onError, onNotice, onRegistered } = options;

  async function register(event: FormEvent<HTMLFormElement>, discovery: CareersDiscovery) {
    event.preventDefault();
    const companyName = form.name.trim() || discovery.company_name;
    if (!companyName) {
      onError("Enter the employer name before registering this recruitment source.");
      return;
    }
    if (
      discovery.detected_adapter === "lever" &&
      ((discovery.outcome !== "success" && discovery.outcome !== "empty") ||
        discovery.complete !== true)
    ) {
      onError(discovery.detail || "The Lever board could not be inspected completely.");
      return;
    }

    setSaving(true);
    onError("");
    onNotice("");
    let employer: Employer | null = null;
    try {
      employer = await scoutApi.createEmployer({
        ...form,
        name: companyName,
        website_url: form.website_url.trim() || null,
        logo_url: getCompanyIconUrl(sourceUrl),
        logo_source_url: sourceUrl,
      });
      const source = await scoutApi.createSource(employer.id, {
        adapter_key: discovery.detected_adapter,
        source_url: discovery.board_url,
        normalized_url: discovery.board_url,
        employer_careers_url: sourceUrl,
        adapter_config: discovery.adapter_config,
        discovery_preview: {
          total_vacancies: discovery.total_vacancies ?? discovery.jobs?.length ?? 0,
          jobs: discovery.jobs ?? [],
        },
      });
      onRegistered({ employer, source });
      onNotice(
        employer.name +
          " added. " +
          (source.discovery_preview?.total_vacancies ?? 0) +
          " vacancies discovered. Extraction remains paused until the source is verified and permission is allowed.",
      );
      await loadWorkspace();
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : "An unexpected error occurred.";
      onError(
        employer
          ? employer.name + " was added, but vacancy import needs attention: " + detail
          : "Could not add the company: " + detail,
      );
      if (employer) void loadWorkspace().catch(() => undefined);
    } finally {
      setSaving(false);
    }
  }

  return { register };
}
