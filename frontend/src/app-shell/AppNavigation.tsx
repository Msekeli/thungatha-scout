import type { FC } from "react";

export type AppPage = "jobs" | "companies" | "add-company";

type AppNavigationProps = {
  activePage: AppPage;
  onSelectPage: (page: AppPage) => void;
};

export const AppNavigation: FC<AppNavigationProps> = ({ activePage, onSelectPage }) => {
  return (
    <nav className="flex items-center gap-1.5" aria-label="Main navigation">
      <button
        type="button"
        className={`rounded-md px-3.5 py-1.5 text-xs font-bold transition-colors ${
          activePage === "jobs" ? "active" : ""
        }`}
        onClick={() => onSelectPage("jobs")}
      >
        Jobs
      </button>
      <button
        type="button"
        className={`rounded-md px-3.5 py-1.5 text-xs font-bold transition-colors ${
          activePage === "companies" ? "active" : ""
        }`}
        onClick={() => onSelectPage("companies")}
      >
        Companies
      </button>
      <button
        type="button"
        className={`rounded-md px-3.5 py-1.5 text-xs font-bold transition-colors ${
          activePage === "add-company" ? "active" : ""
        }`}
        onClick={() => onSelectPage("add-company")}
      >
        + Add company
      </button>
    </nav>
  );
};
