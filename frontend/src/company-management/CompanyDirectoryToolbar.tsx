import { Plus, Search, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Props = {
  count: number;
  searchQuery: string;
  statusFilter: string;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onAddCompany: () => void;
};

export function CompanyDirectoryToolbar(props: Props) {
  return (
    <>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-cyan-300">
            Employer directory
          </p>
          <h3 className="mt-1 text-lg font-bold text-white">
            Companies <span className="ml-1 text-sm font-medium text-slate-500">{props.count}</span>
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            Manage employers and the recruitment sources they publish through.
          </p>
        </div>
        <Button
          type="button"
          onClick={props.onAddCompany}
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
            value={props.searchQuery}
            onChange={(event) => props.onSearchChange(event.target.value)}
            placeholder="Search companies…"
            aria-label="Search companies"
            className="h-10 border-slate-700 bg-slate-950/70 pl-9 text-white placeholder:text-slate-500 focus-visible:ring-cyan-400"
          />
        </div>
        <Select value={props.statusFilter} onValueChange={props.onStatusFilterChange}>
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
    </>
  );
}
