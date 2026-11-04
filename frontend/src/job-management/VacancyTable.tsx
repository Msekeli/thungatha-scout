import type { FC } from "react";
import type { Vacancy } from "../shared-contracts/vacancy-contracts";

type VacancyTableProps = {
  vacancies: Vacancy[];
  onOpenVacancy: (vacancy: Vacancy) => void;
  onOpenCompany: (employerId: string) => void;
  openingVacancyId: string | null;
  loading: boolean;
};

export const VacancyTable: FC<VacancyTableProps> = ({
  vacancies,
  onOpenVacancy,
  onOpenCompany,
  openingVacancyId,
  loading,
}) => {
  if (loading) return <div className="empty">Loading jobs…</div>;
  if (vacancies.length === 0) {
    return (
      <div className="empty">
        <strong>No jobs found</strong>
        <span>Try adjusting your filters or extract new jobs.</span>
      </div>
    );
  }

  return (
    <div className="jobs-table-wrap">
      <table className="jobs-table">
        <thead>
          <tr>
            <th>Position</th>
            <th>Company</th>
            <th>Location</th>
            <th>Review status</th>
            <th>Last seen</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {vacancies.map((vacancy) => (
            <tr key={vacancy.id}>
              <td>
                <strong>{vacancy.title}</strong>
                {vacancy.department && <small>{vacancy.department}</small>}
              </td>
              <td>
                <button
                  type="button"
                  className="text-link"
                  onClick={() => onOpenCompany(vacancy.employer_id)}
                >
                  {vacancy.employer_name}
                </button>
              </td>
              <td>{vacancy.location_text || "Not specified"}</td>
              <td>
                <span className={`review-state ${vacancy.review_status}`}>
                  {vacancy.review_status.replace("_", " ")}
                </span>
              </td>
              <td>{new Date(vacancy.last_seen_at).toLocaleDateString()}</td>
              <td>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="button secondary"
                    onClick={() => onOpenVacancy(vacancy)}
                    disabled={openingVacancyId === vacancy.id}
                  >
                    {openingVacancyId === vacancy.id ? "Opening…" : "Review"}
                  </button>
                  <a
                    href={vacancy.application_url}
                    target="_blank"
                    rel="noreferrer"
                    className="button secondary text-cyan-800"
                  >
                    Apply ↗
                  </a>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
