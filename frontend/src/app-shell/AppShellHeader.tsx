import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export type AppPage = "jobs" | "operations" | "companies" | "add-company";

type AppShellHeaderProps = {
  activePage: AppPage;
  onSelectPage: (page: AppPage) => void;
  onRefresh: () => void;
  refreshing: boolean;
};

const pageHeading: Record<AppPage, { eyebrow: string; title: string }> = {
  jobs: { eyebrow: "Vacancy records", title: "Dashboard" },
  operations: { eyebrow: "Operations overview", title: "Ingestion Operations" },
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
    <header className="-mx-4 -mt-4 flex min-h-[76px] flex-wrap items-center justify-between gap-3 border-b border-border bg-card px-4 py-3 text-card-foreground shadow-sm md:-mx-8 md:px-8">
      <div className="flex min-w-0 items-center">
        <img
          src="/branding/logo.svg"
          alt="Thungatha Scout"
          className="h-11 w-auto max-w-[180px] object-contain"
        />
      </div>

      <div className="flex-1 text-center">
        <p className="text-[9px] font-bold uppercase tracking-[.2em] text-muted-foreground">
          {heading.eyebrow}
        </p>
        <h2 className="font-semibold text-foreground">{heading.title}</h2>
      </div>

      <nav className="flex items-center gap-1.5" aria-label="Main navigation">
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={activePage === "jobs" ? "bg-accent text-accent-foreground" : "text-muted-foreground"}
          onClick={() => onSelectPage("jobs")}
        >
          Dashboard
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={activePage === "operations" ? "bg-accent text-accent-foreground" : "text-muted-foreground"}
          onClick={() => onSelectPage("operations")}
        >
          Operations
        </Button>
        <Button type="button" size="sm" variant="ghost" className={activePage === "companies" || activePage === "add-company" ? "bg-accent text-accent-foreground" : "text-muted-foreground"} onClick={() => onSelectPage("companies")}>Companies</Button>
        {(activePage === "jobs" || activePage === "operations") && (
          <Button
            type="button"
            size="icon"
            variant="ghost"
            className="text-muted-foreground"
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
