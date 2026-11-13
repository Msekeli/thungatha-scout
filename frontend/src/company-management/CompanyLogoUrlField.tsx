import { ImagePlus, Link2 } from "lucide-react";
import { Input } from "@/components/ui/input";

type Props = {
  value: string;
  failed: boolean;
  onChange: (value: string) => void;
  onPreviewError: () => void;
};

export function CompanyLogoUrlField({ value, failed, onChange, onPreviewError }: Props) {
  return (
    <div className="grid gap-2">
      <label className="flex items-center gap-2 text-sm font-medium text-foreground">
        <ImagePlus className="h-4 w-4 text-muted-foreground" />
        Company logo URL
      </label>
      <div className="flex min-w-0 flex-col gap-3 sm:flex-row">
        <div className="flex h-20 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-border bg-muted/40 p-2">
          {value.trim() && !failed ? (
            <img
              src={value.trim()}
              alt="Company logo preview"
              className="h-full w-full object-contain"
              onError={onPreviewError}
            />
          ) : (
            <ImagePlus className="h-7 w-7 text-muted-foreground" />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <Input
            type="url"
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder="https://example.com/assets/logo"
            aria-label="Company logo URL"
          />
          <p className="mt-1.5 flex items-start gap-1.5 text-xs text-muted-foreground">
            <Link2 className="mt-0.5 h-3 w-3 shrink-0" />
            Paste the direct public image address. Scout stores the URL, not the image file.
          </p>
          {value.trim() && failed && (
            <p className="mt-1 text-xs text-destructive">
              This address could not be previewed. Check that it points to a publicly accessible
              image.
            </p>
          )}
          {value.trim() && (
            <button
              type="button"
              className="mt-2 text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground"
              onClick={() => onChange("")}
            >
              Clear logo URL
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
