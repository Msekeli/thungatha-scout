import { Building2, BriefcaseBusiness, ExternalLink, Globe2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";

type Props = {
  employer: Employer;
  sources: EmployerSource[];
  selected: boolean;
  onSelect: (employer: Employer) => void;
};

export function CompanyDirectoryCard({ employer, sources, selected, onSelect }: Props) {
  const statusTone = employer.status === "approved" ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-300"
    : employer.status === "needs_review" || employer.status === "rejected" ? "border-rose-400/30 bg-rose-400/10 text-rose-300"
    : "border-amber-400/30 bg-amber-400/10 text-amber-200";
  const careersUrl = sources.find((source) => source.employer_careers_url)?.employer_careers_url
    ?? employer.website_url;
  return (
    <article className={`group overflow-hidden rounded-2xl border bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800/90 shadow-lg shadow-black/20 transition-all hover:-translate-y-1 hover:border-cyan-400/50 hover:shadow-cyan-950/40 ${selected ? "border-cyan-400 ring-1 ring-cyan-400/40" : "border-slate-700"}`}>
      <div className="h-1 bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500" />
      <Button type="button" variant="ghost" aria-pressed={selected}
        onClick={() => onSelect(employer)}
        className="h-auto w-full items-start justify-start gap-3 rounded-none px-4 pb-3 pt-4 text-left font-normal hover:bg-white/[0.04]">
        <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl border border-cyan-300/20 bg-cyan-400/10 text-cyan-300">
          {employer.logo_url ? <img src={employer.logo_url} alt="" className="h-8 w-8 rounded-lg bg-white object-contain p-1" /> : <Building2 className="h-5 w-5" />}
        </span>
        <span className="min-w-0 flex-1">
          <strong className="block truncate text-sm font-semibold text-white">{employer.name}</strong>
          <span className="mt-1 flex items-center gap-2 text-xs text-slate-400">
            <BriefcaseBusiness className="h-3.5 w-3.5 text-cyan-300" />
            {sources.length} registered source{sources.length === 1 ? "" : "s"}
          </span>
          <span className="mt-3 flex flex-wrap gap-1.5">
            <Badge className="border-violet-300/20 bg-violet-400/10 text-[10px] text-violet-200 hover:bg-violet-400/10">{employer.organization_type.replaceAll("_", " ")}</Badge>
            <Badge className={`border text-[10px] capitalize hover:bg-transparent ${statusTone}`}>{employer.status.replaceAll("_", " ")}</Badge>
          </span>
        </span>
      </Button>
      <div className="grid gap-2 border-t border-slate-700/80 bg-black/20 px-4 py-3">
        {careersUrl && <a href={careersUrl} target="_blank" rel="noreferrer" title={careersUrl}
          className="flex min-w-0 items-center gap-2 text-xs text-cyan-300 hover:text-cyan-100">
          <Globe2 className="h-3.5 w-3.5 shrink-0" /><span className="truncate">Official careers page</span><ExternalLink className="ml-auto h-3 w-3 shrink-0" />
        </a>}
        {sources.map((source) => <a key={source.id} href={source.source_url} target="_blank" rel="noreferrer" title={source.source_url}
          className="flex min-w-0 items-center gap-2 text-xs text-slate-300 hover:text-white">
          <span className="grid h-5 w-5 shrink-0 place-items-center rounded bg-slate-700 text-[9px] font-bold uppercase text-cyan-200">{source.adapter_key === "greenhouse" ? "G" : "W"}</span>
          <span className="truncate">{source.adapter_key === "greenhouse" ? "Greenhouse board" : "Workday board"}</span>
          <ExternalLink className="ml-auto h-3 w-3 shrink-0" />
        </a>)}
        {!careersUrl && !sources.length && <span className="text-xs text-slate-500">No recruitment links registered</span>}
      </div>
    </article>
  );
}
