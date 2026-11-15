import { BriefcaseBusiness, LogOut, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
export type AppPage = "jobs" | "operations" | "companies" | "add-company";
type AppShellHeaderProps = {
  activePage: AppPage;
  onSelectPage: (page: AppPage) => void;
  onRefresh: () => void;
  refreshing: boolean;
  onFetchJobs: () => void;
  fetching: boolean;
  fetchDisabled: boolean;
  onSignOut: () => void;
  administratorEmail: string;
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
  onFetchJobs,
  fetching,
  fetchDisabled,
  onSignOut,
  administratorEmail,
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
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {heading.eyebrow}
        </p>
        <h2 className="font-semibold text-foreground">{heading.title}</h2>
      </div>
      <nav className="flex items-center gap-1.5" aria-label="Main navigation">
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={
            activePage === "jobs" ? "bg-accent text-accent-foreground" : "text-muted-foreground"
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
            activePage === "operations"
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground"
          }
          onClick={() => onSelectPage("operations")}
        >
          Operations
        </Button>
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className={
            activePage === "companies" || activePage === "add-company"
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground"
          }
          onClick={() => onSelectPage("companies")}
        >
          Companies
        </Button>
        {activePage === "jobs" && (
          <Button
            type="button"
            size="sm"
            className="bg-scout-cyan text-scout-navy hover:brightness-95"
            onClick={onFetchJobs}
            disabled={fetchDisabled || fetching}
          >
            <BriefcaseBusiness className="mr-1 h-3.5 w-3.5" />
            {fetching ? "Fetching jobs…" : "Fetch jobs"}
          </Button>
        )}
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
        <div
          className="ml-2 hidden max-w-[180px] truncate border-l border-border pl-3 text-xs text-muted-foreground xl:block"
          title={administratorEmail}
        >
          {administratorEmail}
        </div>
        <Button
          type="button"
          size="icon"
          variant="ghost"
          className="text-muted-foreground"
          title="Sign out"
          aria-label="Sign out"
          onClick={onSignOut}
        >
          <LogOut className="h-4 w-4" />
        </Button>
      </nav>
    </header>
  );
}
