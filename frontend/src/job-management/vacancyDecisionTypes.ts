import type { Vacancy } from "../api";

export type PreviousVacancyDecision = {
  vacancyId: string;
  status: Vacancy["review_status"];
  reason: string | null;
};

export type VacancyDecisionState = {
  current: PreviousVacancyDecision | null;
};
