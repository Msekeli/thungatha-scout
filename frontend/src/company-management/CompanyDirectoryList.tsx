import type { FC } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Employer } from "../api";

type CompanyDirectoryListProps = {
  employers: Employer[];
  selectedEmployerId: string;
  onSelectEmployer: (employer: Employer) => void;
  emptyMessage?: string;
};

export const CompanyDirectoryList: FC<CompanyDirectoryListProps> = ({
  employers,
  selectedEmployerId,
  onSelectEmployer,
  emptyMessage = "No companies matched your criteria.",
}) => {
  if (employers.length === 0) {
    return <div className="py-8 text-center text-xs text-muted-foreground">{emptyMessage}</div>;
  }

  return (
    <div className="flex flex-col gap-1">
      {employers.map((employer) => (
        <Button
          key={employer.id}
          type="button"
          variant="ghost"
          aria-pressed={selectedEmployerId === employer.id}
          className={`h-auto w-full justify-start gap-3 rounded-lg border p-2 text-left font-normal shadow-none transition-colors hover:bg-accent ${
            selectedEmployerId === employer.id
              ? "border-ring bg-accent"
              : "border-transparent bg-transparent"
          }`}
          onClick={() => onSelectEmployer(employer)}
        >
          {employer.logo_url ? (
            <img
              src={employer.logo_url}
              alt={`${employer.name} logo`}
              className="h-[38px] w-[38px] shrink-0 rounded-lg border border-border bg-card object-contain"
            />
          ) : (
            <span className="grid h-[34px] w-[34px] shrink-0 place-items-center rounded-lg bg-secondary font-extrabold text-secondary-foreground">
              {employer.name.slice(0, 1).toUpperCase()}
            </span>
          )}
          <span className="min-w-0">
            <strong className="block truncate text-xs font-semibold text-foreground">
              {employer.name}
            </strong>
            <small className="text-[10px] text-muted-foreground">
              {employer.city || "Location not confirmed"}
            </small>
          </span>
          <Badge variant="outline" className="ml-auto shrink-0 capitalize">
            {employer.status.replaceAll("_", " ")}
          </Badge>
        </Button>
      ))}
    </div>
  );
};
