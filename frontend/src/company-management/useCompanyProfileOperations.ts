import { useCallback } from "react";
import type { Dispatch, SetStateAction } from "react";
import { scoutApi } from "../api";
import type { Employer } from "../api";

type EmployerStatus = "approved" | "needs_review" | "rejected" | "inactive";

type UseCompanyProfileOperationsOptions = {
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
}: UseCompanyProfileOperationsOptions) {
  const updateStatus = useCallback(
    async (status: EmployerStatus) => {
      if (!employer) return;

      setSaving(true);
      onError("");
      try {
        const updated = await scoutApi.updateEmployerStatus(employer.id, status);
        setEmployers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
        onNotice(`${updated.name} marked ${status.replaceAll("_", " ")}.`);
      } catch (reason) {
        onError(reason instanceof Error ? reason.message : "Could not update company status.");
      } finally {
        setSaving(false);
      }
    },
    [employer, setEmployers, setSaving, onNotice, onError],
  );

  const deleteCompany = useCallback(async () => {
    if (!employer) return;
    if (
      !window.confirm(
        `Permanently delete ${employer.name}? Companies with sources or vacancies cannot be deleted.`,
      )
    ) {
      return;
    }

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

  const saveBranding = useCallback(async () => {
    if (!employer) return;

    setSaving(true);
    onError("");
    try {
      const updated = await scoutApi.updateEmployerBranding(
        employer.id,
        logoUrl.trim(),
        logoSourceUrl.trim(),
      );
      setEmployers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      onNotice("Company logo details saved.");
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : "Could not save company logo details.");
    } finally {
      setSaving(false);
    }
  }, [employer, logoUrl, logoSourceUrl, setEmployers, setSaving, onNotice, onError]);

  return { updateStatus, deleteCompany, saveBranding };
}
