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
  discovery: CareersDiscovery | null;
  form: EmployerRegistrationForm;
  sourceUrl: string;
  loadWorkspace: () => Promise<void>;
  setSaving: (value: boolean) => void;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
  onRegistered: (result: { employer: Employer; source: EmployerSource }) => void;
};

export function useEmployerRegistration({
  discovery,
  form,
  sourceUrl,
  loadWorkspace,
  setSaving,
  onError,
  onNotice,
  onRegistered,
}: UseEmployerRegistrationOptions) {
  async function register(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!discovery || !form.name.trim()) return;

    setSaving(true);
    onError("");
    onNotice("");
    try {
      const employer = await scoutApi.createEmployer({
        ...form,
        website_url: form.website_url.trim() || null,
      });
      const source = await scoutApi.createSource(employer.id, {
        adapter_key: discovery.detected_adapter,
        source_url: discovery.board_url,
        normalized_url: discovery.board_url,
        employer_careers_url: sourceUrl,
        adapter_config: { slug: discovery.board_token },
      });
      await loadWorkspace();
      onRegistered({ employer, source });
      onNotice(employer.name + " added. Greenhouse extraction started.");
      const run = await scoutApi.extractSource(source.id);
      await loadWorkspace();
      onNotice(
        employer.name + ": " + run.jobs_received + " vacancies retrieved; extraction " + run.outcome + ".",
      );
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not register employer and source.");
      await loadWorkspace();
    } finally {
      setSaving(false);
    }
  }

  return { register };
}
