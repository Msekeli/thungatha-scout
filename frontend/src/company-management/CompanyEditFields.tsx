import { Input } from "@/components/ui/input";
import { CompanyOrganizationTypeSelect } from "./CompanyOrganizationTypeSelect";

export type CompanyEditFieldValues = {
  name: string;
  legal_name: string;
  website_url: string;
  organization_type: string;
  city: string;
  province: string;
  country: string;
};

type Props = {
  fields: CompanyEditFieldValues;
  onChange: (key: keyof CompanyEditFieldValues, value: string) => void;
};

export function CompanyEditFields({ fields, onChange }: Props) {
  const field = (label: string, key: keyof CompanyEditFieldValues, placeholder = "") => (
    <label className="grid gap-1.5 text-sm font-medium">
      {label}
      <Input value={fields[key]} placeholder={placeholder}
        onChange={(event) => onChange(key, event.target.value)} />
    </label>
  );
  return (
    <>
      {field("Company name", "name")}
      {field("Legal name", "legal_name")}
      {field("Official website", "website_url", "https://company.com")}
      <CompanyOrganizationTypeSelect value={fields.organization_type}
        onChange={(value) => onChange("organization_type", value)} />
      <div className="grid gap-3 sm:grid-cols-3">
        {field("City", "city")}
        {field("Province", "province")}
        {field("Country", "country")}
      </div>
    </>
  );
}
