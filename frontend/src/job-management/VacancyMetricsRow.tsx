import type { FC } from "react";
import type { Vacancy } from "../shared-contracts/vacancy-contracts";

type VacancyMetricsRowProps = {
  employerCount: number;
  vacancies: Vacancy[];
};

export const VacancyMetricsRow: FC<VacancyMetricsRowProps> = ({ employerCount, vacancies }) => {
  const verifiedCount = vacancies.filter((item) => item.review_status === "verified").length;

  return (
    <section className="metric-row">
      <div className="metric-card">
        <span>Companies</span>
        <strong>{employerCount}</strong>
      </div>
      <div className="metric-card">
        <span>Collected vacancies</span>
        <strong>{vacancies.length}</strong>
      </div>
      <div className="metric-card">
        <span>Verified vacancies</span>
        <strong>{verifiedCount}</strong>
      </div>
    </section>
  );
};
