import type { FC } from "react";
import { Plus, Search, SlidersHorizontal } from "lucide-react";
import type { Employer, EmployerSource } from "../api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CompanyDirectoryList } from "./CompanyDirectoryList";

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

export const CompanyDirectoryPanel: FC<Props> = ({
  employers,
  sources,
  selectedEmployerId,
  searchQuery,
  statusFilter,
  onSearchChange,
  onStatusFilterChange,
  onSelectEmployer,
  onAddCompany,
}) => {
  const visible = employers.filter(
    (item) =>
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      (statusFilter === "all" || item.status === statusFilter),
  );
  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70 p-4 shadow-xl shadow-black/20 sm:p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-300">
            Employer directory
          </p>
          <h3 className="mt-1 text-lg font-bold text-white">
            Companies{" "}
            <span className="ml-1 text-sm font-medium text-slate-500">{employers.length}</span>
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            Manage employers and the recruitment sources they publish through.
          </p>
        </div>
        <Button
          type="button"
          onClick={onAddCompany}
          className="bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-950/40 hover:bg-cyan-400"
        >
          <Plus className="mr-1.5 h-4 w-4" /> Add company
        </Button>
      </div>
      <div className="mb-4 grid gap-2 sm:grid-cols-[minmax(0,1fr)_190px]">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <Input
            type="search"
            value={searchQuery}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search companies…"
            aria-label="Search companies"
            className="h-10 border-slate-700 bg-slate-950/70 pl-9 text-white placeholder:text-slate-500 focus-visible:ring-cyan-400"
          />
        </div>
        <Select value={statusFilter} onValueChange={onStatusFilterChange}>
          <SelectTrigger
            aria-label="Filter companies by status"
            className="h-10 border-slate-700 bg-slate-950/70 text-slate-200"
          >
            <SlidersHorizontal className="mr-2 h-4 w-4 text-slate-400" />
            <SelectValue placeholder="All statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="discovered">Discovered</SelectItem>
            <SelectItem value="pending_review">Pending review</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="needs_review">Needs review</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="mb-3 flex items-center justify-between text-xs text-slate-500">
        <span>
          Showing <strong className="text-slate-300">{visible.length}</strong> of {employers.length}{" "}
          employers
        </span>
        <span className="hidden sm:inline">Select a card to manage its sources and details</span>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto pr-1">
        <CompanyDirectoryList
          employers={visible}
          sources={sources}
          selectedEmployerId={selectedEmployerId}
          onSelectEmployer={onSelectEmployer}
          emptyMessage={
            employers.length ? "No companies match your search." : "No companies registered yet."
          }
        />
      </div>
    </section>
  );
};
