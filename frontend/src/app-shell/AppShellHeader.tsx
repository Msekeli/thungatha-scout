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

  const navigationButtonClass = (isActive: boolean) =>
    isActive
      ? "bg-white text-scout-navy hover:bg-white/90 hover:text-scout-navy"
      : "text-white/80 hover:bg-white/10 hover:text-white";

  return (
    <header className="-mx-4 -mt-4 flex min-h-[76px] flex-wrap items-center justify-between gap-3 bg-gradient-to-r from-[#070d18] via-[#10152b] to-[#17122b] border-b border-cyan-400/20 px-4 py-[14px] text-white shadow-md md:-mx-8 md:px-8">
      <div className="flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/10 text-scout-cyan shadow-inner">
          <Radar className="h-6 w-6" />
        </span>
        <div>
          <p className="mb-0.5 text-[9px] font-bold tracking-[.2em] text-white/65">
            THUNGATHA / OPERATIONS
          </p>
          <h1 className="text-lg font-bold tracking-tight text-white">Scout</h1>
        </div>
      </div>

      <div className="flex-1 text-center">
        <p className="text-[9px] font-bold uppercase tracking-[.2em] text-scout-cyan">
          {heading.eyebrow}
        </p>
        <h2 className="text-lg font-bold tracking-tight text-white">{heading.title}</h2>
      </div>

      <nav className="flex items-center gap-1.5" aria-label="Main navigation">
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={navigationButtonClass(activePage === "jobs")}
          onClick={() => onSelectPage("jobs")}
        >
          Dashboard
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={navigationButtonClass(activePage !== "jobs")}
          onClick={() => onSelectPage("companies")}
        >
          Companies
        </Button>
        {activePage === "jobs" && (
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="text-white/80 hover:bg-white/10 hover:text-white"
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
