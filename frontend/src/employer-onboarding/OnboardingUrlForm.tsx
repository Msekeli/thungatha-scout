import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type OnboardingUrlFormProps = {
  sourceUrl: string;
  onChangeSourceUrl: (url: string) => void;
  atsKey: string;
  onChangeAtsKey: (key: string) => void;
  onDetect: () => void;
  inspecting: boolean;
};

export function OnboardingUrlForm({
  sourceUrl,
  onChangeSourceUrl,
  atsKey,
  onChangeAtsKey,
  onDetect,
  inspecting,
}: OnboardingUrlFormProps) {
  return (
    <div className="grid gap-3">
      <label className="grid gap-1 text-xs font-medium text-muted-foreground">
        Careers / jobs listing URL
        <Input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="https://company.com/jobs"
          required
        />
      </label>

      <label className="grid gap-1 text-xs font-medium text-muted-foreground">
        ATS platform
        <Select value={atsKey} onValueChange={onChangeAtsKey}>
          <SelectTrigger className="h-9">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="greenhouse">Greenhouse</SelectItem>
            <SelectItem value="workday" disabled>
              Workday — coming next
            </SelectItem>
          </SelectContent>
        </Select>
      </label>

      <Button
        type="button"
        size="sm"
        variant="outline"
        className="w-fit"
        onClick={onDetect}
        disabled={inspecting || !sourceUrl.trim()}
      >
        {inspecting ? "Detecting ATS and inspecting jobs…" : "Detect ATS & preview jobs"}
      </Button>
    </div>
  );
}
