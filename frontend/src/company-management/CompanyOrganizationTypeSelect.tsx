import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

type Props = { value: string; onChange: (value: string) => void };

export function CompanyOrganizationTypeSelect({ value, onChange }: Props) {
  return (
    <label className="grid gap-1.5 text-sm font-medium">
      Organisation type
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger><SelectValue /></SelectTrigger>
        <SelectContent>
          <SelectItem value="direct_employer">Direct employer</SelectItem>
          <SelectItem value="recruitment_agency">Recruitment agency</SelectItem>
          <SelectItem value="staffing_company">Staffing company</SelectItem>
          <SelectItem value="hybrid">Hybrid</SelectItem>
          <SelectItem value="other">Other</SelectItem>
          <SelectItem value="unresolved">Unresolved</SelectItem>
        </SelectContent>
      </Select>
    </label>
  );
}
