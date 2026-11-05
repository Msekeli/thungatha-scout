import type { Employer } from "../api";
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
};

export function VacancyRecordsToolbar({
  selectedEmployerId,
  onEmployerChange,
  employers,
}: VacancyRecordsToolbarProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-border bg-card p-3">
      <h3 className="mr-auto text-sm font-bold text-primary">Vacancy records</h3>
      <Select value={selectedEmployerId} onValueChange={onEmployerChange}>
        <SelectTrigger
          aria-label="Filter vacancies by company"
          className="h-8 w-[160px] border-input bg-background text-xs text-foreground"
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
    </div>
  );
}
