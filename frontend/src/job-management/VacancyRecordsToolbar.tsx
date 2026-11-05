import type { Employer } from "../api";
import type { VacancyLocationScope } from "../shared-contracts/vacancy-contracts";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";

type VacancyRecordsToolbarProps = {
  selectedEmployerId: string;
  onEmployerChange: (value: string) => void;
  employers: Employer[];
  locationScope: VacancyLocationScope;
  onLocationChange: (value: VacancyLocationScope) => void;
  totalVacancies: number;
  loadedVacancies: number;
};

export function VacancyRecordsToolbar({
  selectedEmployerId, onEmployerChange, employers, locationScope,
  onLocationChange, totalVacancies, loadedVacancies,
}: VacancyRecordsToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border bg-card p-3">
      <div className="mr-auto">
        <h3 className="text-sm font-bold text-primary">Vacancy records</h3>
        <p className="text-xs text-muted-foreground" aria-live="polite">
          {totalVacancies.toLocaleString()} matching vacancies · Showing {loadedVacancies.toLocaleString()}
        </p>
      </div>
      <Select value={locationScope} onValueChange={(value) => onLocationChange(value as VacancyLocationScope)}>
        <SelectTrigger aria-label="Filter vacancies by location" className="h-8 w-[145px] border-input bg-background text-xs text-foreground">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="cape_town">Cape Town + Stellenbosch</SelectItem>
          <SelectItem value="south_africa">South Africa</SelectItem>
        </SelectContent>
      </Select>
      <Select value={selectedEmployerId} onValueChange={onEmployerChange}>
        <SelectTrigger aria-label="Filter vacancies by company" className="h-8 w-[160px] border-input bg-background text-xs text-foreground">
          <SelectValue placeholder="All companies" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All companies</SelectItem>
          {employers.map((employer) => (
            <SelectItem key={employer.id} value={employer.id}>{employer.name}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
