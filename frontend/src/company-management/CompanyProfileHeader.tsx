import type { FC } from "react";
import { Badge } from "@/components/ui/badge";
import type { Employer } from "../api";

type CompanyProfileHeaderProps = {
  employer: Employer;
  jobsCount: number;
  sourcesCount: number;
};

export const CompanyProfileHeader: FC<CompanyProfileHeaderProps> = ({
  employer,
  jobsCount,
  sourcesCount,
}) => {
  return (
    <div className="mb-4 rounded-xl border border-scout-navy bg-scout-navy p-4 text-white shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold tracking-widest text-scout-cyan">
            COMPANY PROFILE
          </p>
          <h3 className="mt-1 truncate text-base font-bold text-white">{employer.name}</h3>
          <p className="mt-1 break-all text-[11px] text-white/65">
            {employer.website_url ? (
              <a
                href={employer.website_url}
                target="_blank"
                rel="noreferrer"
                className="text-scout-cyan underline-offset-2 hover:underline"
              >
                {employer.website_url}
              </a>
            ) : (
              "Official website not supplied"
            )}
          </p>
        </div>
        <Badge variant="outline" className="shrink-0 border-white/30 text-white capitalize">
          {employer.status.replaceAll("_", " ")}
        </Badge>
      </div>
      <div className="mt-4 flex gap-7 border-t border-white/15 pt-3">
        <div className="grid gap-0.5">
          <strong className="text-base font-bold text-white">{jobsCount}</strong>
          <span className="text-[10px] text-white/60">Jobs collected</span>
        </div>
        <div className="grid gap-0.5">
          <strong className="text-base font-bold text-white">{sourcesCount}</strong>
          <span className="text-[10px] text-white/60">Sources registered</span>
        </div>
      </div>
    </div>
  );
};
