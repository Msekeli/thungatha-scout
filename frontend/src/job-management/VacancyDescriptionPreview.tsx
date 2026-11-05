import type { Vacancy } from "../api";
import { decodeGreenhouseContent } from "./html-content-decoder";

export function VacancyDescriptionPreview({ vacancy }: { vacancy: Vacancy }) {
  return (
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
  );
}
