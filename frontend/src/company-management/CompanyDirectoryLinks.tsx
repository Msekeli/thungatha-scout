import { ExternalLink, Globe2 } from "lucide-react";
import type { Employer, EmployerSource } from "../api";

type Props = { employer: Employer; sources: EmployerSource[] };
const visibleUrl = (value: string) => value.replace(/^https?:\/\//, "");

export function CompanyDirectoryLinks({ employer, sources }: Props) {
  const careersSource = sources.find((source) => source.employer_careers_url);
  const careersUrl = careersSource?.employer_careers_url ?? employer.website_url;
  const careersLabel = careersSource ? "Careers" : "Website";
  return (
    <div className="scout-company-card__footer">
      {careersUrl && (
        <a
          href={careersUrl}
          target="_blank"
          rel="noreferrer"
          title={careersUrl}
          className="scout-company-link"
        >
          <Globe2 className="h-3.5 w-3.5 shrink-0" />
          <span className="shrink-0">{careersLabel}</span>
          <span className="truncate scout-company-link__url">{visibleUrl(careersUrl)}</span>
          <ExternalLink className="ml-auto h-3 w-3 shrink-0" />
        </a>
      )}
      {sources.map((source) => (
        <a
          key={source.id}
          href={source.source_url}
          target="_blank"
          rel="noreferrer"
          title={source.source_url}
          className="scout-company-link"
        >
          <span className="grid h-5 w-5 shrink-0 place-items-center rounded bg-slate-700 text-[9px] font-bold uppercase text-cyan-200">
            {source.adapter_key === "greenhouse" ? "G" : "W"}
          </span>
          <span className="shrink-0">
            {source.adapter_key === "greenhouse" ? "Greenhouse" : "Workday"}
          </span>
          <span className="truncate scout-company-link__url">{visibleUrl(source.source_url)}</span>
          <ExternalLink className="ml-auto h-3 w-3 shrink-0" />
        </a>
      ))}
      {!careersUrl && !sources.length && (
        <span className="text-xs scout-company-muted">No recruitment links registered</span>
      )}
    </div>
  );
}
