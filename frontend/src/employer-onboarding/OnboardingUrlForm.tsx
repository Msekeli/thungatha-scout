import type { FC, FormEvent } from "react";

type OnboardingUrlFormProps = {
  sourceUrl: string;
  onChangeSourceUrl: (url: string) => void;
  atsKey: string;
  onChangeAtsKey: (key: string) => void;
  onDetect: (event: FormEvent) => void;
  inspecting: boolean;
};

export const OnboardingUrlForm: FC<OnboardingUrlFormProps> = ({
  sourceUrl,
  onChangeSourceUrl,
  atsKey,
  onChangeAtsKey,
  onDetect,
  inspecting,
}) => {
  return (
    <div className="grid gap-3">
      <label>
        Careers / jobs listing URL
        <input
          type="url"
          value={sourceUrl}
          onChange={(event) => onChangeSourceUrl(event.target.value)}
          placeholder="https://company.com/jobs"
          required
        />
      </label>

      <label>
        ATS platform
        <select
          value={atsKey}
          onChange={(event) => onChangeAtsKey(event.target.value)}
        >
          <option value="greenhouse">Greenhouse</option>
          <option value="workday" disabled>
            Workday — coming next
          </option>
        </select>
      </label>

      <button
        type="button"
        className="button secondary"
        onClick={onDetect}
        disabled={inspecting || !sourceUrl.trim()}
      >
        {inspecting
          ? "Detecting ATS and inspecting jobs…"
          : "Detect ATS & preview jobs"}
      </button>
    </div>
  );
};
