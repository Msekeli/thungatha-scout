import type { FormEvent } from "react";
import { scoutApi } from "../api";
import type { CareersDiscovery, Employer, EmployerSource } from "../api";

type EmployerRegistrationForm = {
  name: string;
  website_url: string;
  organization_type: string;
  city: string;
  province: string;
  country: string;
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
    if (!companyName) return;

    setSaving(true);
    onError("");
    onNotice("");
    let employer: Employer | null = null;
    try {
      employer = await scoutApi.createEmployer({
        ...form,
        name: companyName,
        website_url: form.website_url.trim() || null,
      });
      const source = await scoutApi.createSource(employer.id, {
        adapter_key: discovery.detected_adapter,
        source_url: discovery.board_url,
        normalized_url: discovery.board_url,
        employer_careers_url: sourceUrl,
        adapter_config: { slug: discovery.board_token },
      });
      onRegistered({ employer, source });
      onNotice(employer.name + " added. Importing vacancies…");
      const extraction = scoutApi.extractSource(source.id);
      const [, run] = await Promise.all([loadWorkspace(), extraction]);
      await loadWorkspace();
      onNotice(employer.name + ": " + run.jobs_received + " vacancies imported successfully.");
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : "An unexpected error occurred.";
      onError(
        employer
          ? employer.name + " was added, but vacancy import needs attention: " + detail
          : "Could not add the company: " + detail,
      );
      if (employer) await loadWorkspace();
    } finally {
      setSaving(false);
    }
  }

  return { register };
}
