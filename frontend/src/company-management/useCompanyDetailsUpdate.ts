import { useCallback } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer } from "../api";

type Values = { name: string; website_url: string | null; organization_type: string };

type Options = {
  employer: Employer | null;
  setEmployers: Dispatch<SetStateAction<Employer[]>>;
  setSaving: (saving: boolean) => void;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useCompanyDetailsUpdate({ employer, setEmployers, setSaving, onNotice, onError }: Options) {
  return useCallback(async (values: Values) => {
    if (!employer) return;
    setSaving(true);
    onError("");
    try {
      const updated = await scoutApi.updateEmployer(employer.id, values);
      setEmployers((current) => current.map((item) => item.id === updated.id ? updated : item));
      onNotice(`${updated.name} details updated.`);
      return true;
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not update company details.");
      return false;
    } finally {
      setSaving(false);
    }
  }, [employer, setEmployers, setSaving, onNotice, onError]);
}
