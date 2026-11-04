import type { FC, FormEvent } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "../components/ui/dialog";

type CompanyBrandingModalProps = {
  isOpen: boolean;
  onClose: () => void;
  logoUrl: string;
  logoSourceUrl: string;
  onChangeLogoUrl: (val: string) => void;
  onChangeLogoSourceUrl: (val: string) => void;
  onSave: () => void;
  saving: boolean;
};

export const CompanyBrandingModal: FC<CompanyBrandingModalProps> = ({
  isOpen,
  onClose,
  logoUrl,
  logoSourceUrl,
  onChangeLogoUrl,
  onChangeLogoSourceUrl,
  onSave,
  saving,
}) => {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSave();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Update Employer Logo</DialogTitle>
          <DialogDescription className="text-xs text-slate-500">
            Provide a direct image URL for the company's verified logo.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="grid gap-3 pt-2">
          <label>
            Logo Image URL
            <input
              type="url"
              value={logoUrl}
              onChange={(e) => onChangeLogoUrl(e.target.value)}
              placeholder="https://example.com/logo.png"
            />
          </label>
          <label>
            Attribution / Source URL (optional)
            <input
              type="url"
              value={logoSourceUrl}
              onChange={(e) => onChangeLogoSourceUrl(e.target.value)}
              placeholder="https://example.com/press-kit"
            />
          </label>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" className="button secondary" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="button primary" disabled={saving}>
              {saving ? "Saving…" : "Save logo"}
            </button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
