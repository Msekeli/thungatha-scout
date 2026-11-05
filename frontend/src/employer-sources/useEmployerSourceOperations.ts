import type { FormEvent, Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer, EmployerSource, GreenhouseInspection } from "../api";

type UseEmployerSourceOperationsOptions = {
  employer: Employer | null;
  sources: EmployerSource[];
  setSources: Dispatch<SetStateAction<EmployerSource[]>>;
  sourceUrl: string;
  setSourceUrl: (value: string) => void;
  editingSourceId: string | null;
  setEditingSourceId: (value: string | null) => void;
  inspection: GreenhouseInspection | null;
  setInspection: (value: GreenhouseInspection | null) => void;
  setSaving: (value: boolean) => void;
  onError: (message: string) => void;
  onNotice: (message: string) => void;
};

export function useEmployerSourceOperations({
  employer,
  sources,
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
}: UseEmployerSourceOperationsOptions) {
  async function saveSource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!employer) return;

    setSaving(true);
    onError("");
    try {
      const payload = {
        adapter_key: editingSourceId
          ? sources.find((source) => source.id === editingSourceId)?.adapter_key
          : "greenhouse",
        source_url: sourceUrl,
        normalized_url: sourceUrl,
        adapter_config: { slug: inspection?.board_token },
      };

      if (editingSourceId) {
        await scoutApi.updateSource(employer.id, editingSourceId, payload);
        setSources(await scoutApi.listSources(employer.id));
        onNotice(
          "Source configuration updated. Its verification and permission states were preserved.",
        );
      } else {
        const created = await scoutApi.createSource(employer.id, {
          ...payload,
          employer_careers_url: employer.website_url ?? null,
        });
        setSources((current) => [...current, created]);
        onNotice("Greenhouse source registered. Verification and permission remain pending.");
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
