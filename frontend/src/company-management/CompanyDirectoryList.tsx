import type { FC } from "react";
import { Globe2, Building2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  selectedEmployerId: string;
  onSelectEmployer: (employer: Employer) => void;
  emptyMessage?: string;
};

export const CompanyDirectoryList: FC<Props> = ({ employers, sources, selectedEmployerId, onSelectEmployer, emptyMessage = "No companies matched your criteria." }) => {
  if (!employers.length) return <div className="rounded-xl border border-dashed border-border py-12 text-center text-sm text-muted-foreground">{emptyMessage}</div>;
  return (
    <div className="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
      {employers.map((employer) => {
        const companySources = sources.filter((source) => source.employer_id === employer.id);
        return (
          <Button key={employer.id} type="button" variant="ghost" aria-pressed={selectedEmployerId === employer.id} onClick={() => onSelectEmployer(employer)}
            className={`h-auto min-h-[116px] min-w-0 items-start justify-start gap-3 rounded-xl border p-3 text-left font-normal shadow-none transition-colors hover:border-ring hover:bg-accent ${selectedEmployerId === employer.id ? "border-ring bg-accent" : "border-border bg-background"}`}>
            {employer.logo_url ? <img src={employer.logo_url} alt="" className="h-10 w-10 shrink-0 rounded-lg border border-border bg-card object-contain p-1" /> : <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-secondary text-secondary-foreground"><Building2 className="h-5 w-5" /></span>}
            <span className="min-w-0 flex-1">
              <strong className="block truncate text-sm font-semibold text-foreground">{employer.name}</strong>
              <span className="mt-1 flex items-center gap-1 truncate text-xs text-muted-foreground"><Globe2 className="h-3 w-3 shrink-0" />{employer.website_url || "Website not supplied"}</span>
              <span className="mt-3 flex flex-wrap gap-1">
                {companySources.length ? companySources.map((source) => <Badge key={source.id} variant="secondary" className="text-[10px] capitalize">{source.adapter_key}</Badge>) : <Badge variant="outline" className="text-[10px]">No job board</Badge>}
                <Badge variant="outline" className="text-[10px] capitalize">{employer.status.replaceAll("_", " ")}</Badge>
              </span>
            </span>
          </Button>
        );
      })}
    </div>
  );
};
