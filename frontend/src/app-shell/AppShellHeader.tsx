import { Radar, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export type AppPage = "jobs" | "companies" | "add-company";

type AppShellHeaderProps = {
  activePage: AppPage;
  onSelectPage: (page: AppPage) => void;
  onRefresh: () => void;
  refreshing: boolean;
};

const pageHeading: Record<AppPage, { eyebrow: string; title: string }> = {
  jobs: { eyebrow: "Operations overview", title: "Ingestion Dashboard" },
  companies: { eyebrow: "Employer directory", title: "Companies" },
  "add-company": { eyebrow: "Employer onboarding", title: "Add a company" },
};

export function AppShellHeader({
  activePage,
  onSelectPage,
  onRefresh,
  refreshing,
}: AppShellHeaderProps) {
  const heading = pageHeading[activePage];

  return (
    <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-3">
      <div className="flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#0b1426] text-cyan-300 shadow-lg shadow-slate-900/20">
          <Radar className="h-6 w-6" />
        </span>
        <div>
          <p className="mb-0.5 text-[9px] font-bold tracking-[.2em] text-slate-500">
            THUNGATHA / OPERATIONS
          </p>
          <h1 className="text-lg font-bold tracking-tight text-[#0b1426]">Scout</h1>
        </div>
      </div>
      <div className="flex-1 text-center">
        <p className="text-[9px] font-bold uppercase tracking-[.2em] text-cyan-700">
          {heading.eyebrow}
        </p>
        <h2 className="text-lg font-bold tracking-tight text-[#0b1426]">{heading.title}</h2>
      </div>
      <nav className="flex items-center gap-1.5" aria-label="Main navigation">
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={
            activePage === "jobs"
              ? "bg-[#0b1426] text-white hover:bg-[#172b46] hover:text-white"
              : "text-slate-600"
          }
          onClick={() => onSelectPage("jobs")}
        >
          Dashboard
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={
            activePage !== "jobs"
              ? "bg-[#0b1426] text-white hover:bg-[#172b46] hover:text-white"
              : "text-slate-600"
          }
          onClick={() => onSelectPage("companies")}
        >
          Companies
        </Button>
        {activePage === "jobs" && (
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="text-slate-600 hover:bg-cyan-50 hover:text-cyan-800"
            title="Refresh dashboard data"
            aria-label="Refresh dashboard data"
            onClick={onRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={refreshing ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
          </Button>
        )}
      </nav>
    </header>
  );
}
