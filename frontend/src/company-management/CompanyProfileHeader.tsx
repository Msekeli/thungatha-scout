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
    <>
      <div className="mb-3 flex items-start justify-between gap-3 border-b border-border pb-3">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold tracking-widest text-muted-foreground">
            COMPANY PROFILE
          </p>
          <h3 className="mt-1 truncate text-base font-bold text-primary">{employer.name}</h3>
          <p className="mt-1 break-all text-[11px] text-muted-foreground">
            {employer.website_url ? (
              <a
                href={employer.website_url}
                target="_blank"
                rel="noreferrer"
                className="text-primary underline-offset-2 hover:underline"
              >
                {employer.website_url}
              </a>
            ) : (
              "Official website not supplied"
            )}
          </p>
        </div>
        <Badge variant="outline" className="shrink-0 capitalize">
          {employer.status.replaceAll("_", " ")}
        </Badge>
      </div>
      <div className="mb-4 flex gap-7 border-y border-border py-3">
        <div className="grid gap-0.5">
          <strong className="text-base font-bold text-primary">{jobsCount}</strong>
          <span className="text-[10px] text-muted-foreground">Jobs collected</span>
        </div>
        <div className="grid gap-0.5">
          <strong className="text-base font-bold text-primary">{sourcesCount}</strong>
          <span className="text-[10px] text-muted-foreground">Sources registered</span>
        </div>
      </div>
    </>
  );
};
