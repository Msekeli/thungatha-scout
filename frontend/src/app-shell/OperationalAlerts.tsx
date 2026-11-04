import { Alert } from "@/components/ui/alert";

type OperationalAlertsProps = {
  error?: string | null;
  notice?: string | null;
};

export function OperationalAlerts({ error, notice }: OperationalAlertsProps) {
  if (!error && !notice) return null;

  return (
    <div className="space-y-2 pt-3" aria-live="polite">
      {error && <Alert variant="destructive">{error}</Alert>}
      {notice && (
        <Alert variant="success" role="status">
          {notice}
        </Alert>
      )}
    </div>
  );
}
