import type { FC } from "react";
import type { Employer, EmployerSource } from "../api";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { CompanyDirectoryList } from "./CompanyDirectoryList";
import { CompanySearchFilters } from "./CompanySearchFilters";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  selectedEmployerId: string;
  searchQuery: string;
  statusFilter: string;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onSelectEmployer: (employer: Employer) => void;
  onAddCompany: () => void;
};

export const CompanyDirectoryPanel: FC<Props> = ({ employers, sources, selectedEmployerId, searchQuery, statusFilter, onSearchChange, onStatusFilterChange, onSelectEmployer, onAddCompany }) => {
  const visibleEmployers = employers.filter((employer) =>
    employer.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
    (statusFilter === "all" || employer.status === statusFilter));
  return (
    <section className="flex min-h-0 min-w-0 flex-col rounded-xl border border-border bg-card p-4 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
        <div><h3 className="text-base font-semibold text-foreground">Company directory</h3><p className="mt-1 text-xs text-muted-foreground">Your registered employers and their recruitment sources.</p></div>
        <Button type="button" size="sm" onClick={onAddCompany}><Plus className="mr-1.5 h-4 w-4" />Add company</Button>
      </div>
      <CompanySearchFilters searchQuery={searchQuery} onSearchChange={onSearchChange} statusFilter={statusFilter} onStatusFilterChange={onStatusFilterChange} />
      <div className="mb-3 text-xs text-muted-foreground">{visibleEmployers.length} of {employers.length} companies</div>
      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        <CompanyDirectoryList employers={visibleEmployers} sources={sources} selectedEmployerId={selectedEmployerId} onSelectEmployer={onSelectEmployer} emptyMessage={employers.length ? "No companies match these filters." : "No companies registered yet."} />
      </div>
    </section>
  );
};
