import type { Vacancy } from "../api";
import { decodeGreenhouseContent } from "./html-content-decoder";

export function VacancyDescriptionPreview({ vacancy }: { vacancy: Vacancy }) {
  return (
    <div>
      <h4 className="mb-2 text-sm font-bold text-primary">Extracted description</h4>
      {vacancy.description ? (
        <iframe
          className="scout-vacancy-description"
          title={"Description for " + vacancy.title}
          sandbox=""
          srcDoc={
            '<!doctype html><html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src https: data:; style-src \'unsafe-inline\';"><meta name="viewport" content="width=device-width, initial-scale=1"><style>html{color-scheme:dark}body{font:14px/1.65 system-ui,sans-serif;color:CanvasText;background:Canvas;margin:18px;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:LinkText}img{max-width:100%;height:auto}ul,ol{padding-left:24px}</style></head><body>' +
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
