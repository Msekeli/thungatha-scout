import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ShieldCheck } from "lucide-react";
import type { Vacancy } from "../api";
import { decodeGreenhouseContent } from "./html-content-decoder";

type VacancyDetailsPanelProps = {
  vacancy: Vacancy | null;
  loading: boolean;
  reviewReason: string;
  saving: boolean;
  onChangeReviewReason: (value: string) => void;
  onClear: () => void;
  onDecision: (status: Vacancy["review_status"]) => void;
  onArchive: () => void;
  onRestore: () => void;
};

const reviewLabel = (status: Vacancy["review_status"]) =>
  ({
    pending: "Pending review",
    needs_verification: "Needs verification",
    verified: "Verified",
    rejected: "Rejected",
  })[status];

export function VacancyDetailsPanel({
  vacancy,
  loading,
  reviewReason,
  saving,
  onChangeReviewReason,
  onClear,
  onDecision,
  onArchive,
  onRestore,
}: VacancyDetailsPanelProps) {
  if (loading) {
    return (
      <div className="grid flex-1 place-content-center text-center text-sm text-muted-foreground">
        Loading vacancy…
      </div>
    );
  }

  if (!vacancy) {
    return (
      <div className="grid flex-1 place-content-center px-6 text-center">
        <p className="text-sm font-semibold text-primary">Select a vacancy record</p>
        <p className="mt-1 max-w-xs text-xs text-muted-foreground">
          Inspect extracted content and resolve records requiring admin attention.
        </p>
      </div>
    );
  }

  const archived = Boolean(vacancy.archived_at);

  return (
    <>
      <div className="flex items-center justify-between gap-3 border-b border-scout-navy bg-scout-navy p-4 text-white">
        <div className="min-w-0">
          <p className="text-[10px] font-medium text-scout-cyan">
            {vacancy.employer_name} · {vacancy.location_text || "Location unknown"}
          </p>
          <h3 className="mt-1 text-sm font-bold">{vacancy.title}</h3>
        </div>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="text-white/75 hover:bg-white/10 hover:text-white"
          onClick={onClear}
        >
          Clear
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-3">
        <Button
          asChild
          type="button"
          size="sm"
          className="bg-scout-cyan text-primary hover:opacity-90"
        >
          <a href={vacancy.application_url} target="_blank" rel="noreferrer">
            Open source listing ↗
          </a>
        </Button>
        <Button asChild size="sm" variant="outline">
          <a href={vacancy.source_url} target="_blank" rel="noreferrer">
            Source record ↗
          </a>
        </Button>
        <Badge
          variant={
            vacancy.review_status === "verified"
              ? "default"
              : vacancy.review_status === "rejected"
                ? "destructive"
                : "secondary"
          }
          className={
            vacancy.review_status === "pending" || vacancy.review_status === "needs_verification"
              ? "bg-warning-surface text-warning hover:bg-warning-surface"
              : ""
          }
        >
          {reviewLabel(vacancy.review_status)}
        </Badge>
      </div>

      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        <div>
          <h4 className="mb-2 text-sm font-bold text-primary">Extracted description</h4>
          {vacancy.description ? (
            <iframe
              className="h-[min(42vh,500px)] min-h-[280px] w-full rounded-lg border border-border bg-card"
              title={"Description for " + vacancy.title}
              sandbox=""
              srcDoc={
                '<!doctype html><html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src https: data:; style-src \'unsafe-inline\';"><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{font:14px/1.65 system-ui,sans-serif;color:#263449;margin:18px;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:#168bb9}img{max-width:100%;height:auto}ul,ol{padding-left:24px}</style></head><body>' +
                decodeGreenhouseContent(vacancy.description) +
                "</body></html>"
              }
            />
          ) : (
            <p className="rounded-lg bg-warning-surface p-4 text-sm text-warning">
              No description was saved by the source. Inspect the source listing.
            </p>
          )}
        </div>

        <section className="rounded-lg border border-border">
          <div className="border-b bg-muted px-3 py-2">
            <h4 className="text-xs font-bold text-primary">Admin review actions</h4>
            <p className="mt-1 text-[10px] text-muted-foreground">
              Pending is the database default; it does not mean automated verification has run.
            </p>
          </div>
          <div className="space-y-3 p-3">
            <label className="grid gap-1 text-xs font-medium text-muted-foreground">
              Decision notes
              <Textarea
                value={reviewReason}
                disabled={archived}
                onChange={(event) => onChangeReviewReason(event.target.value)}
                placeholder="Record the reason for your decision"
                aria-label="Vacancy decision notes"
              />
            </label>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                size="sm"
                variant="ghost"
                disabled={saving || archived}
                onClick={() => onDecision("verified")}
                className="bg-success text-white shadow-sm hover:brightness-95"
              >
                <ShieldCheck className="h-4 w-4" />
                Mark verified
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={saving || archived}
                onClick={() => onDecision("needs_verification")}
              >
                Needs verification
              </Button>
              <Button
                type="button"
                size="sm"
                variant="destructive"
                disabled={saving || archived}
                onClick={() => onDecision("rejected")}
              >
                Reject record
              </Button>
              {archived ? (
                <Button type="button" size="sm" disabled={saving} onClick={onRestore}>
                  Restore
                </Button>
              ) : (
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={saving}
                  onClick={onArchive}
                >
                  Archive
                </Button>
              )}
            </div>
          </div>
        </section>

        <details className="rounded-lg border border-border">
          <summary className="cursor-pointer px-3 py-2 text-xs font-semibold text-muted-foreground">
            Publishing payload preview
          </summary>
          <pre className="max-h-64 overflow-auto border-t bg-muted p-3 text-xs">
            {JSON.stringify(
              {
                title: vacancy.title,
                company: vacancy.employer_name,
                location: vacancy.location_text,
                review_status: vacancy.review_status,
                review_reason: vacancy.review_reason,
                application_url: vacancy.application_url,
                source_url: vacancy.source_url,
              },
              null,
              2,
            )}
          </pre>
        </details>
      </div>
    </>
  );
}
