import type { Vacancy } from "../api";
import { decodeGreenhouseContent } from "./html-content-decoder";

function readThemeToken(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function VacancyDescriptionPreview({ vacancy }: { vacancy: Vacancy }) {
  const surface = readThemeToken("--scout-surface");
  const foreground = readThemeToken("--foreground");
  const link = readThemeToken("--scout-link");
  const content = vacancy.description ? decodeGreenhouseContent(vacancy.description) : "";
  return (
    <div>
      <h4 className="mb-2 text-sm font-bold text-primary">Extracted description</h4>
      {content ? (
        <iframe
          className="scout-vacancy-description"
          title={"Description for " + vacancy.title}
          sandbox=""
          srcDoc={
            '<!doctype html><html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src https: data:; style-src \'unsafe-inline\';"><meta name="viewport" content="width=device-width, initial-scale=1"><style>' +
            'html{color-scheme:dark}body{font:14px/1.65 system-ui,sans-serif;color:hsl(' + foreground +
            ');background:' + surface + ';margin:18px;overflow-wrap:anywhere}h1,h2,h3{line-height:1.3}a{color:' +
            link + '}img{max-width:100%;height:auto}ul,ol{padding-left:24px}</style></head><body>' +
            content +
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
