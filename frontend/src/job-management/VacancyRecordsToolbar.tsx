import { Button } from "@/components/ui/button";
import type { Employer } from "../api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type VacancyRecordsToolbarProps = {
  showArchived: boolean;
  onShowArchivedChange: (showArchived: boolean) => void;
  reviewFilter: string;
  onReviewFilterChange: (value: string) => void;
  selectedEmployerId: string;
  onEmployerChange: (value: string) => void;
  employers: Employer[];
  onRefresh: () => void;
  loading: boolean;
};

export function VacancyRecordsToolbar({
  showArchived,
  onShowArchivedChange,
  reviewFilter,
  onReviewFilterChange,
  selectedEmployerId,
  onEmployerChange,
  employers,
  onRefresh,
  loading,
}: VacancyRecordsToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border bg-muted/70 p-3">
      <h3 className="mr-auto text-sm font-bold text-primary">
        {showArchived ? "Archived vacancies" : "Vacancy records"}
      </h3>
      <Select
        value={showArchived ? "archived" : "active"}
        onValueChange={(value) => onShowArchivedChange(value === "archived")}
      >
        <SelectTrigger
          aria-label="Choose active or archived vacancies"
          className="h-8 w-[125px] bg-card text-xs"
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="active">Active records</SelectItem>
          <SelectItem value="archived">Archived</SelectItem>
        </SelectContent>
      </Select>
      <Select value={reviewFilter} onValueChange={onReviewFilterChange}>
        <SelectTrigger
          aria-label="Filter vacancies by review state"
          className="h-8 w-[145px] bg-card text-xs"
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All review states</SelectItem>
          <SelectItem value="pending">Pending</SelectItem>
          <SelectItem value="needs_verification">Needs verification</SelectItem>
          <SelectItem value="verified">Verified</SelectItem>
          <SelectItem value="rejected">Rejected</SelectItem>
        </SelectContent>
      </Select>
      <Select value={selectedEmployerId} onValueChange={onEmployerChange}>
        <SelectTrigger
          aria-label="Filter vacancies by company"
          className="h-8 w-[140px] bg-card text-xs"
        >
          <SelectValue placeholder="All companies" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All companies</SelectItem>
          {employers.map((employer) => (
            <SelectItem key={employer.id} value={employer.id}>
              {employer.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="h-8 bg-card"
        onClick={onRefresh}
        disabled={loading}
      >
        Refresh
      </Button>
    </div>
  );
}
