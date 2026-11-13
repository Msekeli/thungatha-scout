import { useCallback } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer } from "../api";

type Options = {
  employer: Employer | null;
  logoUrl: string;
  logoSourceUrl: string;
  setEmployers: Dispatch<SetStateAction<Employer[]>>;
  onDeleted: () => void;
  setSaving: (saving: boolean) => void;
  onNotice: (message: string) => void;
  onError: (message: string) => void;
};

export function useCompanyProfileOperations({
  employer,
  logoUrl,
  logoSourceUrl,
  setEmployers,
  onDeleted,
  setSaving,
  onNotice,
  onError,
}: Options) {
  const deleteCompany = useCallback(async () => {
    if (!employer) return;
    setSaving(true);
    onError("");
    try {
      await scoutApi.deleteEmployer(employer.id);
      setEmployers((current) => current.filter((item) => item.id !== employer.id));
      onDeleted();
      onNotice("Company deleted.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not delete company.");
    } finally {
      setSaving(false);
    }
  }, [employer, setEmployers, onDeleted, setSaving, onNotice, onError]);

  const saveBranding = useCallback(
    async (nextLogoUrl?: string) => {
      if (!employer) return false;
      setSaving(true);
      onError("");
      try {
        const updated = await scoutApi.updateEmployerBranding(
          employer.id,
          (nextLogoUrl ?? logoUrl).trim(),
          logoSourceUrl.trim(),
          employer.logo_type ?? "unverified",
        );
        setEmployers((current) => current.map((item) => (item.id === updated.id ? { ...item, ...updated, vacancy_count: item.vacancy_count } : item)));
        onNotice("Company profile updated.");
        return true;
      } catch (reason) {
        onError(reason instanceof Error ? reason.message : "Could not save company logo details.");
        return false;
      } finally {
        setSaving(false);
      }
    },
    [employer, logoUrl, logoSourceUrl, setEmployers, setSaving, onNotice, onError],
  );

  return { deleteCompany, saveBranding };
}
