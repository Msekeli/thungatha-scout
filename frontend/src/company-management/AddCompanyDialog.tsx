import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { EmployerOnboardingPanel } from "../employer-onboarding/EmployerOnboardingPanel";
import type { useScoutAppState } from "../app-state/useScoutAppState";
import type { useEmployerOnboardingController } from "../employer-onboarding/useEmployerOnboardingController";

type Props = {
  state: ReturnType<typeof useScoutAppState>;
  onboarding: ReturnType<typeof useEmployerOnboardingController>;
};

export function AddCompanyDialog({ state, onboarding }: Props) {
  const open = state.page === "add-company";
  return (
    <Dialog
      open={open}
      onOpenChange={(value) => {
        if (!value) {
          state.setPage("companies");
          state.setSourceUrl("");
        }
      }}
    >
      <DialogContent className="scout-company-add-dialog">
        <DialogHeader>
          <DialogTitle className="scout-company-heading">Add a company</DialogTitle>
          <DialogDescription className="scout-company-dialog-copy">
            Paste a supported careers-board URL. Add the employer's official website to enable logo
            discovery when the ATS hosts the careers page.
          </DialogDescription>
        </DialogHeader>
        <EmployerOnboardingPanel
          sourceUrl={state.sourceUrl}
          onChangeSourceUrl={state.setSourceUrl}
          inspecting={onboarding.inspecting}
          form={state.form}
          onChangeCompanyName={(value) => state.setForm((current) => ({ ...current, name: value }))}
          onChangeWebsiteUrl={(value) =>
            state.setForm((current) => ({ ...current, website_url: value }))
          }
          saving={state.saving}
          onSubmit={onboarding.submit}
          onCancel={() => {
            state.setPage("companies");
            state.setSourceUrl("");
          }}
          duplicate={onboarding.duplicate}
          onOpenExisting={onboarding.openExistingCompany}
        />
      </DialogContent>
    </Dialog>
  );
}
