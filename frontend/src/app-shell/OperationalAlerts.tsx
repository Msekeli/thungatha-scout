type OperationalAlertsProps = {
  error?: string | null;
  notice?: string | null;
};

export function OperationalAlerts({ error, notice }: OperationalAlertsProps) {
  if (!error && !notice) return null;

  return (
    <div className="space-y-2 pt-3" aria-live="polite">
      {error && (
        <div
          className="rounded-md border border-border bg-[var(--danger-surface)] px-3 py-2.5 text-sm text-[var(--danger-text)]"
          role="alert"
        >
          {error}
        </div>
      )}
      {notice && (
        <div
          className="rounded-md border border-border bg-[var(--success-surface)] px-3 py-2.5 text-sm text-[var(--success-text)]"
          role="status"
        >
          {notice}
        </div>
      )}
    </div>
  );
}
