import { Button } from "@/components/ui/button";
import type { EmployerDuplicateMatch } from "./findEmployerDuplicate";

type EmployerDuplicateNoticeProps = {
  duplicate: EmployerDuplicateMatch | null;
  onOpenExisting: (employerId: string) => void;
};

export function EmployerDuplicateNotice({
  duplicate,
  onOpenExisting,
}: EmployerDuplicateNoticeProps) {
  if (!duplicate) return null;
  const isSource = duplicate.kind === "source";
  return (
    <div
      role={isSource ? "alert" : undefined}
      className={
        isSource
          ? "rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm"
          : "rounded-lg border border-blue-500/40 bg-blue-500/10 p-3 text-sm"
      }
    >
      <p className="font-semibold">
        {isSource
          ? "This recruitment source has already been added."
          : "This company is already in Scout."}
      </p>
      <p className="mt-1">
        {isSource
          ? `${duplicate.employer.name} already has this careers URL registered.`
          : `This URL will be added as another recruitment source under ${duplicate.employer.name}. Scout will not create a second company.`}
      </p>
      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-3"
        onClick={() => onOpenExisting(duplicate.employer.id)}
      >
        Open existing company
      </Button>
    </div>
  );
}
