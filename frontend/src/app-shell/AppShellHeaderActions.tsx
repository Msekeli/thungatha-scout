import { BriefcaseBusiness, LogOut, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { AppPage } from "./AppShellHeader";

export type AppShellHeaderActionsProps = {
  activePage: AppPage;
  onRefresh: () => void;
  refreshing: boolean;
  onFetchJobs: () => void;
  fetching: boolean;
  fetchDisabled: boolean;
  onSignOut: () => void;
  administratorEmail: string;
};

export function AppShellHeaderActions({
  activePage,
  onRefresh,
  refreshing,
  onFetchJobs,
  fetching,
  fetchDisabled,
  onSignOut,
  administratorEmail,
}: AppShellHeaderActionsProps) {
  return (
    <>
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
    </>
  );
}
