import type { SourceDiscoveryPreview } from "../shared-contracts/employer-contracts";

type Props = { preview: SourceDiscoveryPreview };

export function CareerPageCrawlPreview({ preview }: Props) {
  if (preview.crawl_complete === undefined) return null;
  const pages = preview.pages ?? [];
  const failed = preview.failed_urls ?? [];
  const skipped = preview.skipped_urls ?? [];

  return (
    <details className="mt-2 rounded-md border border-border p-2 text-xs">
      <summary className="cursor-pointer font-semibold text-foreground">
        Crawl evidence · {preview.crawl_complete ? "complete" : "incomplete"}
        {" · "}
        {preview.pages_observed ?? pages.length} pages ·{" "}
        {preview.vacancies_found ?? preview.total_vacancies} vacancies
      </summary>
      <div className="mt-2 grid gap-2 text-muted-foreground">
        {pages.map((page) => (
          <div key={page.requested_url} className="grid gap-1 border-t border-border pt-2">
            <strong className="break-all text-foreground">
              {page.page_title || page.final_url}
            </strong>
            <span>
              {page.outcome} · HTTP {page.status_code} · {page.vacancies_found} vacancies
            </span>
            <a
              className="break-all underline"
              href={page.final_url}
              target="_blank"
              rel="noreferrer"
            >
              {page.final_url}
            </a>
            {page.discovered_links.length > 0 && (
              <span>{page.discovered_links.length} career links discovered</span>
            )}
          </div>
        ))}
        {failed.length > 0 && (
          <p className="break-all text-destructive">Failed: {failed.join(", ")}</p>
        )}
        {skipped.length > 0 && <p className="break-all">Skipped: {skipped.join(", ")}</p>}
      </div>
    </details>
  );
}
