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
import { ADAPTER_LABELS, SUPPORTED_ADAPTERS } from "../shared-contracts/adapter-contracts";

type Props = {
  searchQuery: string;
  sourceFilter: string;
  onSearchChange: (value: string) => void;
  onSourceFilterChange: (value: string) => void;
  onAddCompany: () => void;
};

export function CompanyDirectoryToolbar(props: Props) {
  return (
    <>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] scout-company-eyebrow">
            Employer directory
          </p>
          <h3 className="mt-1 text-lg font-bold scout-company-heading">Companies</h3>
          <p className="mt-1 text-xs scout-company-description">
            Manage employers and the recruitment sources they publish through.
          </p>
        </div>
        <Button type="button" onClick={props.onAddCompany} className="scout-company-toolbar-button">
          <Plus className="mr-1.5 h-4 w-4" /> Add company
        </Button>
      </div>
      <div className="mb-4 grid gap-2 sm:grid-cols-[minmax(0,1fr)_190px]">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 scout-company-muted" />
          <Input
            type="search"
            value={props.searchQuery}
            onChange={(event) => props.onSearchChange(event.target.value)}
            placeholder="Search companies…"
            aria-label="Search companies"
            className="scout-company-field pl-9 focus-visible:ring-ring"
          />
        </div>
        <Select value={props.sourceFilter} onValueChange={props.onSourceFilterChange}>
          <SelectTrigger
            aria-label="Filter companies by recruitment platform"
            className="scout-company-filter"
          >
            <SlidersHorizontal className="mr-2 h-4 w-4 scout-company-description" />
            <SelectValue placeholder="All job boards" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All job boards</SelectItem>
            {SUPPORTED_ADAPTERS.map((adapter) => (
              <SelectItem key={adapter} value={adapter}>
                {ADAPTER_LABELS[adapter].label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </>
  );
}
