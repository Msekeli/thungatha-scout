import { useState, useMemo, useRef, useCallback } from "react";
import type { Vacancy } from "../shared-contracts/vacancy-contracts";
import { vacancyApiClient } from "../api-services/vacancy-api-client";

export function useVacancyManagement(
  initialVacancies: Vacancy[],
  onNotice: (msg: string) => void,
  onError: (msg: string) => void,
) {
  const [vacancies, setVacancies] = useState<Vacancy[]>(initialVacancies);
  const [archivedVacancies, setArchivedVacancies] = useState<Vacancy[]>([]);
  const [showArchived, setShowArchived] = useState(false);
  const [selectedEmployerId, setSelectedEmployerId] = useState("all");
  const [reviewFilter, setReviewFilter] = useState("all");
  const [selectedVacancy, setSelectedVacancy] = useState<Vacancy | null>(null);
  const [openingVacancyId, setOpeningVacancyId] = useState<string | null>(null);
  const [reviewReason, setReviewReason] = useState("");
  const [saving, setSaving] = useState(false);
  const requestRef = useRef(0);

  const displayedVacancies = useMemo(() => {
    const list = showArchived ? archivedVacancies : vacancies;
    return list.filter((v) => {
      const matchEmp = selectedEmployerId === "all" || v.employer_id === selectedEmployerId;
      const matchReview = reviewFilter === "all" || v.review_status === reviewFilter;
      return matchEmp && matchReview;
    });
  }, [showArchived, archivedVacancies, vacancies, selectedEmployerId, reviewFilter]);

  const loadArchived = useCallback(async () => {
    try {
      const archived = await vacancyApiClient.listArchivedVacancies();
      setArchivedVacancies(archived);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not load archived jobs.");
    }
  }, [onError]);

  const toggleArchived = useCallback(() => {
    setShowArchived((prev) => {
      const next = !prev;
      if (next) void loadArchived();
      return next;
    });
  }, [loadArchived]);

  const openVacancy = useCallback(async (vacancy: Vacancy) => {
    const seq = ++requestRef.current;
    setOpeningVacancyId(vacancy.id);
    setSelectedVacancy(vacancy);
    setReviewReason(vacancy.review_reason || "");
    try {
      const fresh = await vacancyApiClient.getVacancy(vacancy.id);
      if (requestRef.current === seq) {
        setSelectedVacancy(fresh);
        setReviewReason(fresh.review_reason || "");
      }
    } catch {
      // Retain optimistic selection
    } finally {
      if (requestRef.current === seq) setOpeningVacancyId(null);
    }
  }, []);

  const saveReview = useCallback(async (status: Vacancy["review_status"], reason: string) => {
    if (!selectedVacancy) return;
    setSaving(true);
    try {
      const updated = await vacancyApiClient.updateVacancyReview(selectedVacancy.id, status, reason);
      setSelectedVacancy(updated);
      setVacancies((prev) => prev.map((v) => (v.id === updated.id ? updated : v)));
      onNotice(`Vacancy marked as ${status.replace("_", " ")}.`);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not update review.");
    } finally {
      setSaving(false);
    }
  }, [selectedVacancy, onNotice, onError]);

  const archive = useCallback(async () => {
    if (!selectedVacancy) return;
    setSaving(true);
    try {
      const archived = await vacancyApiClient.archiveVacancy(selectedVacancy.id, reviewReason);
      setVacancies((prev) => prev.filter((v) => v.id !== archived.id));
      setArchivedVacancies((prev) => [archived, ...prev]);
      setSelectedVacancy(null);
      onNotice("Vacancy moved to archive.");
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not archive vacancy.");
    } finally {
      setSaving(false);
    }
  }, [selectedVacancy, reviewReason, onNotice, onError]);

  const restore = useCallback(async () => {
    if (!selectedVacancy) return;
    setSaving(true);
    try {
      const restored = await vacancyApiClient.restoreVacancy(selectedVacancy.id);
      setArchivedVacancies((prev) => prev.filter((v) => v.id !== restored.id));
      setVacancies((prev) => [restored, ...prev]);
      setSelectedVacancy(null);
      onNotice("Vacancy restored to active list.");
    } catch (err) {
      onError(err instanceof Error ? err.message : "Could not restore vacancy.");
    } finally {
      setSaving(false);
    }
  }, [selectedVacancy, onNotice, onError]);

  return {
    vacancies, setVacancies, displayedVacancies, showArchived, toggleArchived,
    selectedEmployerId, setSelectedEmployerId, reviewFilter, setReviewFilter,
    selectedVacancy, setSelectedVacancy, openingVacancyId, reviewReason,
    setReviewReason, saving, openVacancy, saveReview, archive, restore,
  };
}
