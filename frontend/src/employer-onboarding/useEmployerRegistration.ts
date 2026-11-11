import type { FormEvent } from "react";
import { scoutApi } from "../api";
import { runEmployerVacancyImport } from "./runEmployerVacancyImport";
import { findEmployerDuplicate } from "./findEmployerDuplicate";
import type { CareersDiscovery, Employer, EmployerSource } from "../api";

type EmployerRegistrationForm = {
  name: string;
  website_url: string;
  organization_type: string;
};
type EmployerRegistrationOptions = {
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

export function useEmployerRegistration(options: EmployerRegistrationOptions) {
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

  async function register(event: FormEvent<HTMLFormElement>, sourceInfo: CareersDiscovery) {
    event.preventDefault();
    const companyName = form.name.trim() || sourceInfo.company_name;
    if (!companyName) {
      onError("Enter the employer name before registering this recruitment source.");
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
    const isNewEmployer = duplicate?.kind !== "employer";
    try {
      employer =
        duplicate?.kind === "employer"
          ? duplicate.employer
          : await scoutApi.createEmployer({
              ...form,
              name: companyName,
              website_url: form.website_url.trim() || null,
              logo_url: null,
              logo_source_url: null,
            });

      const source = await scoutApi.createSource(employer.id, {
        adapter_key: sourceInfo.detected_adapter,
        source_url: sourceInfo.board_url,
        normalized_url: sourceInfo.board_url,
        employer_careers_url: sourceUrl,
        adapter_config: sourceInfo.adapter_config,
        discovery_preview: null,
      });
      onRegistered({ employer, source });
      onNotice(
        employer.name +
          " added. Vacancy extraction and logo discovery are running in the background.",
      );
      void scoutApi
        .discoverEmployerLogo(employer.id)
        .then(() => loadWorkspace())
        .catch(() => undefined);
      void runEmployerVacancyImport(source.id, employer.name, {
        loadWorkspace,
        onError,
        onNotice,
      });
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : "An unexpected error occurred.";
      if (employer && isNewEmployer) {
        await scoutApi.deleteEmployer(employer.id).catch(() => undefined);
      }
      onError("Could not add " + (employer?.name ?? companyName) + ": " + detail);
    } finally {
      setSaving(false);
    }
  }
  return { register };
}
