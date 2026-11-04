type OperationalAlertsProps = {
  error?: string | null;
  notice?: string | null;
};

export function OperationalAlerts({ error, notice }: OperationalAlertsProps) {
  return (
    <div className="space-y-2 pt-3" aria-live="polite">
      {error && (
        <div
          className="rounded-md border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-800"
          role="alert"
        >
          {error}
        </div>
      )}
      {notice && (
        <div
          className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-800"
          role="status"
        >
          {notice}
        </div>
      )}
    </div>
  );
}
