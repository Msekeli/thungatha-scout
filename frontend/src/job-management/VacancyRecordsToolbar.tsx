import type { Employer } from "../api";
import type { VacancyAgeFilter, VacancyLocationScope } from "../shared-contracts/vacancy-contracts";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type VacancyRecordsToolbarProps = {
  selectedEmployerId: string;
  onEmployerChange: (value: string) => void;
  employers: Employer[];
  ageFilter: VacancyAgeFilter;
  onAgeFilterChange: (value: VacancyAgeFilter) => void;
  locationScope: VacancyLocationScope;
  onLocationChange: (value: VacancyLocationScope) => void;
  totalVacancies: number;
  loadedVacancies: number;
};

export function VacancyRecordsToolbar({
  selectedEmployerId,
  onEmployerChange,
  employers,
  locationScope,
  ageFilter,
  onAgeFilterChange,
  onLocationChange,
  totalVacancies,
  loadedVacancies,
}: VacancyRecordsToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border bg-card p-3">
      <div className="mr-auto">
        <h3 className="text-sm font-bold text-primary">Vacancy records</h3>
        <p className="text-xs text-muted-foreground" aria-live="polite">
          {totalVacancies.toLocaleString()} matching vacancies · Showing{" "}
          {loadedVacancies.toLocaleString()}
        </p>
      </div>
      <Select
        value={ageFilter}
        onValueChange={(value) => onAgeFilterChange(value as VacancyAgeFilter)}
      >
        <SelectTrigger
          aria-label="Filter vacancies by age"
          className="h-8 w-[150px] border-input bg-background text-xs text-foreground"
        >
          <SelectValue placeholder="All vacancies" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All vacancies</SelectItem>
          <SelectItem value="new">New · last 24 hours</SelectItem>
          <SelectItem value="old">Old · 8+ days</SelectItem>
          <SelectItem value="8_14">8–14 days</SelectItem>
          <SelectItem value="15_30">15–30 days</SelectItem>
          <SelectItem value="over_30">Over 30 days</SelectItem>
          <SelectItem value="undated">No date available</SelectItem>
        </SelectContent>
      </Select>
      <Select
        value={locationScope}
        onValueChange={(value) => onLocationChange(value as VacancyLocationScope)}
      >
        <SelectTrigger
          aria-label="Filter vacancies by location"
          className="h-8 w-[145px] border-input bg-background text-xs text-foreground"
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="cape_town">Cape Town</SelectItem>
          <SelectItem value="western_cape">Western Cape</SelectItem>
          <SelectItem value="south_africa">South Africa</SelectItem>
        </SelectContent>
      </Select>
      <Select value={selectedEmployerId} onValueChange={onEmployerChange}>
        <SelectTrigger
          aria-label="Filter vacancies by company"
          className="h-8 w-[160px] border-input bg-background text-xs text-foreground"
        >
          <SelectValue placeholder="All companies" />
        </SelectTrigger>
        <SelectContent className="max-h-[min(34rem,var(--radix-select-content-available-height))]">
          <SelectItem value="all">All companies</SelectItem>
          {employers.map((employer) => (
            <SelectItem key={employer.id} value={employer.id}>
              {employer.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
