import { Input } from "@/components/ui/input";

type OnboardingUrlFormProps = {
  companyName: string;
  onChangeCompanyName: (name: string) => void;
  sourceUrl: string;
  onChangeSourceUrl: (url: string) => void;
};

export function OnboardingUrlForm({
  companyName,
  onChangeCompanyName,
  sourceUrl,
  onChangeSourceUrl,
}: OnboardingUrlFormProps) {
  return (
    <div className="grid gap-5">
      <label className="scout-company-form-label">
        Official careers page URL
        <Input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="https://company.com/careers"
          className="scout-company-field h-11"
          required
        />
        <span className="scout-company-form-help">
          Paste the employer's careers or jobs page, not an individual vacancy link.
        </span>
      </label>

      <label className="scout-company-form-label">
        Company name
        <Input
          value={companyName}
          onChange={(event) => onChangeCompanyName(event.target.value)}
          placeholder="Enter company name"
          className="h-11 border-slate-700 bg-slate-950 text-white placeholder:text-slate-400"
        />
        <span className="scout-company-form-help">
          Leave blank to use the employer name detected from its careers source.
        </span>
      </label>
    </div>
  );
}
