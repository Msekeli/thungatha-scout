import { useState, useMemo, useCallback } from "react";
import type { Employer, CompanyStatus } from "../shared-contracts/employer-contracts";
import { employerApiClient } from "../api-services/employer-api-client";

export function useCompanyManagement(
  initialEmployers: Employer[],
  onNotice: (msg: string) => void,
  onError: (msg: string) => void,
) {
  const [employers, setEmployers] = useState<Employer[]>(initialEmployers);
  const [selectedEmployerId, setSelectedEmployerId] = useState<string>("all");
  const [companyQuery, setCompanyQuery] = useState("");
  const [companyStatusFilter, setCompanyStatusFilter] = useState("all");
  const [brandingModalOpen, setBrandingModalOpen] = useState(false);
  const [deletionDialogOpen, setDeletionDialogOpen] = useState(false);
  const [logoUrl, setLogoUrl] = useState("");
  const [logoSourceUrl, setLogoSourceUrl] = useState("");
  const [saving, setSaving] = useState(false);

  const selectedEmployer = useMemo(
    () => employers.find((e) => e.id === selectedEmployerId) ?? null,
    [employers, selectedEmployerId],
  );

  const visibleEmployers = useMemo(() => {
    return employers.filter((e) => {
      const matchQuery = !companyQuery.trim() || e.name.toLowerCase().includes(companyQuery.toLowerCase());
      const matchStatus = companyStatusFilter === "all" || e.status === companyStatusFilter;
      return matchQuery && matchStatus;
    });
  }, [employers, companyQuery, companyStatusFilter]);

  const openBranding = useCallback(() => {
    if (!selectedEmployer) return;
    setLogoUrl(selectedEmployer.logo_url || "");
    setLogoSourceUrl(selectedEmployer.logo_source_url || "");
    setBrandingModalOpen(true);
  }, [selectedEmployer]);

  const saveBranding = useCallback(async () => {
    if (!selectedEmployer) return;
    setSaving(true);
    try {
      const updated = await employerApiClient.updateEmployerBranding(selectedEmployer.id, logoUrl, logoSourceUrl);
      setEmployers((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
      setBrandingModalOpen(false);
      onNotice("Company branding updated successfully.");
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not update logo.");
    } finally {
      setSaving(false);
    }
  }, [selectedEmployer, logoUrl, logoSourceUrl, onNotice, onError]);

  const updateStatus = useCallback(async (status: CompanyStatus) => {
    if (!selectedEmployer) return;
    setSaving(true);
    try {
      const updated = await employerApiClient.updateEmployerStatus(selectedEmployer.id, status as any);
      setEmployers((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
      onNotice(`Company marked as ${status.replace("_", " ")}.`);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not update status.");
    } finally {
      setSaving(false);
    }
  }, [selectedEmployer, onNotice, onError]);

  const confirmDelete = useCallback(async () => {
    if (!selectedEmployer) return;
    setSaving(true);
    try {
      await employerApiClient.deleteEmployer(selectedEmployer.id);
      setEmployers((prev) => prev.filter((e) => e.id !== selectedEmployer.id));
      setSelectedEmployerId("all");
      setDeletionDialogOpen(false);
      onNotice("Company deleted successfully.");
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not delete company.");
    } finally {
      setSaving(false);
    }
  }, [selectedEmployer, onNotice, onError]);

  return {
    employers, setEmployers, selectedEmployerId, setSelectedEmployerId,
    selectedEmployer, companyQuery, setCompanyQuery, companyStatusFilter,
    setCompanyStatusFilter, visibleEmployers, brandingModalOpen, setBrandingModalOpen,
    deletionDialogOpen, setDeletionDialogOpen, logoUrl, setLogoUrl,
    logoSourceUrl, setLogoSourceUrl, saving, openBranding, saveBranding,
    updateStatus, confirmDelete,
  };
}
