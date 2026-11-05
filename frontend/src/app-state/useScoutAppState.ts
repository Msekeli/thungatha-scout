import { useCallback, useState } from "react";
import type { EmployerSource } from "../api";

export type ScoutPage = "jobs" | "companies" | "add-company";

export const emptyEmployer = {
  name: "",
  website_url: "",
  organization_type: "unresolved",
  city: "Cape Town",
  province: "Western Cape",
  country: "South Africa",
};

export function useScoutAppState() {
  const [page, setPage] = useState<ScoutPage>("jobs");
  const [showArchived, setShowArchived] = useState(false);
  const [reviewFilter, setReviewFilter] = useState("all");
  const [logoUrl, setLogoUrl] = useState("");
  const [logoSourceUrl, setLogoSourceUrl] = useState("");
  const [companyQuery, setCompanyQuery] = useState("");
  const [companyStatusFilter, setCompanyStatusFilter] = useState("all");
  const [selectedEmployerId, setSelectedEmployerId] = useState("all");
  const [sources, setSources] = useState<EmployerSource[]>([]);
  const [form, setForm] = useState(emptyEmployer);
  const [sourceUrl, setSourceUrl] = useState("");
  const [editingSourceId, setEditingSourceId] = useState<string | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const dismissError = useCallback(() => setError(""), []);
  const dismissNotice = useCallback(() => setNotice(""), []);

  return {
    page,
    setPage,
    showArchived,
    setShowArchived,
    reviewFilter,
    setReviewFilter,
    logoUrl,
    setLogoUrl,
    logoSourceUrl,
    setLogoSourceUrl,
    companyQuery,
    setCompanyQuery,
    companyStatusFilter,
    setCompanyStatusFilter,
    selectedEmployerId,
    setSelectedEmployerId,
    sources,
    setSources,
    form,
    setForm,
    sourceUrl,
    setSourceUrl,
    editingSourceId,
    setEditingSourceId,
    extracting,
    setExtracting,
    saving,
    setSaving,
    error,
    setError,
    notice,
    setNotice,
    dismissError,
    dismissNotice,
  };
}
