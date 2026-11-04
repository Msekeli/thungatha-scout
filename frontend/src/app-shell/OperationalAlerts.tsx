import { useEffect } from "react";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Undo2, X } from "lucide-react";

type OperationalAlertsProps = {
  error?: string | null;
  notice?: string | null;
  canUndo?: boolean;
  onUndo?: () => void;
  onDismissError: () => void;
  onDismissNotice: () => void;
};

export function OperationalAlerts({
  error,
  notice,
  canUndo = false,
  onUndo,
  onDismissError,
  onDismissNotice,
}: OperationalAlertsProps) {
  useEffect(() => {
    if (!notice) return;
    const timeout = window.setTimeout(onDismissNotice, 5000);
    return () => window.clearTimeout(timeout);
  }, [notice, onDismissNotice]);

  useEffect(() => {
    if (!error) return;
    const timeout = window.setTimeout(onDismissError, 8000);
    return () => window.clearTimeout(timeout);
  }, [error, onDismissError]);

  if (!error && !notice) return null;

  return (
    <div className="pointer-events-none fixed right-4 top-[88px] z-[100] flex w-[min(420px,calc(100vw-2rem))] flex-col gap-2">
      {error && (
        <Alert
          variant="destructive"
          className="pointer-events-auto flex min-h-0 items-center justify-between gap-3 rounded-lg bg-white px-3 py-2 text-sm shadow-xl shadow-black/25"
        >
          <span className="min-w-0 flex-1">{error}</span>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="h-7 w-7 shrink-0 text-current hover:bg-black/5"
            aria-label="Dismiss error"
            onClick={onDismissError}
          >
            <X className="h-4 w-4" />
          </Button>
        </Alert>
      )}
      {notice && (
        <Alert
          variant="success"
          role="status"
          className="pointer-events-auto flex min-h-0 items-center justify-between gap-3 rounded-lg bg-white px-3 py-2 text-sm shadow-xl shadow-black/25"
        >
          <span className="min-w-0 flex-1">{notice}</span>
          <div className="flex shrink-0 items-center gap-1">
            {canUndo && onUndo && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-current hover:bg-black/5"
                onClick={onUndo}
              >
                <Undo2 className="mr-1 h-3.5 w-3.5" />
                Undo
              </Button>
            )}
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-current hover:bg-black/5"
              aria-label="Dismiss notification"
              onClick={onDismissNotice}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </Alert>
      )}
    </div>
  );
}
