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
      <label className="grid gap-2 text-sm font-medium text-slate-700">
        Official careers page URL
        <Input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="https://company.com/careers"
          className="h-11 border-slate-300 bg-white text-slate-900 placeholder:text-slate-400"
          required
        />
        <span className="text-xs font-normal text-slate-500">
          Paste the employer's careers or jobs page, not an individual vacancy link.
        </span>
      </label>

      <label className="grid gap-2 text-sm font-medium text-slate-700">
        Company name
        <Input
          value={companyName}
          onChange={(event) => onChangeCompanyName(event.target.value)}
          placeholder="Enter company name"
          className="h-11 border-slate-300 bg-white text-slate-900 placeholder:text-slate-400"
        />
        <span className="text-xs font-normal text-slate-500">
          Leave blank to use the employer name detected from its careers source.
        </span>
      </label>
    </div>
  );
}
