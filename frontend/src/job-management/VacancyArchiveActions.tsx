import type { FC, FormEvent } from "react";

type VacancyArchiveActionsProps = {
  isArchived: boolean;
  reason: string;
  onChangeReason: (value: string) => void;
  onArchive: () => void;
  onRestore: () => void;
  saving: boolean;
};

export const VacancyArchiveActions: FC<VacancyArchiveActionsProps> = ({
  isArchived,
  reason,
  onChangeReason,
  onArchive,
  onRestore,
  saving,
}) => {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (isArchived) {
      onRestore();
    } else {
      onArchive();
    }
  };

  return (
    <form className="archive-actions-panel" onSubmit={handleSubmit}>
      <label>
        {isArchived ? "Archived reason" : "Archive reason (optional)"}
        <input
          type="text"
          value={reason}
          onChange={(event) => onChangeReason(event.target.value)}
          placeholder={
            isArchived ? "Restoring vacancy" : "Role filled or cancelled"
          }
        />
      </label>
      <div className="flex justify-end gap-2">
        {isArchived ? (
          <button
            type="submit"
            className="button secondary text-emerald-700"
            disabled={saving}
          >
            {saving ? "Restoring…" : "Restore vacancy"}
          </button>
        ) : (
          <button
            type="submit"
            className="button secondary text-red-700"
            disabled={saving}
          >
            {saving ? "Archiving…" : "Archive vacancy"}
          </button>
        )}
      </div>
    </form>
  );
};
