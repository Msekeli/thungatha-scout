import type { FormEvent, Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer, EmployerSource, SourceInspection } from "../api";

type Options = {
  employer: Employer | null;
  setSources: Dispatch<SetStateAction<EmployerSource[]>>;
  sourceUrl: string;
  setSourceUrl: (value: string) => void;
  editingSourceId: string | null;
  setEditingSourceId: (value: string | null) => void;
  inspection: SourceInspection | null;
  setInspection: (value: SourceInspection | null) => void;
  setSaving: (value: boolean) => void;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export function useEmployerSourceOperations({
  employer,
  setSources,
  sourceUrl,
  setSourceUrl,
  editingSourceId,
  setEditingSourceId,
  inspection,
  setInspection,
  setSaving,
  onError,
  onNotice,
}: Options) {
  async function saveSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!employer) return;
    setSaving(true);
    onError("");
    try {
      const payload = {
        adapter_key: inspection?.detected_adapter,
        source_url: inspection?.board_url ?? sourceUrl,
        normalized_url: inspection?.board_url ?? sourceUrl,
        adapter_config: inspection?.adapter_config ?? {},
      };
      if (editingSourceId) {
        await scoutApi.updateSource(employer.id, editingSourceId, payload);
        setSources(await scoutApi.listSources(employer.id));
        onNotice("Source configuration updated.");
      } else {
        const created = await scoutApi.createSource(employer.id, {
          ...payload,
          employer_careers_url: employer.website_url ?? null,
        });
        setSources((current) => [...current, created]);
        onNotice(`${inspection?.detected_adapter ?? "Recruitment"} source registered.`);
      }
      setEditingSourceId(null);
      setSourceUrl("");
      setInspection(null);
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not register source.");
    } finally {
      setSaving(false);
    }
  }
  return { saveSource };
}
