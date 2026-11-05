import { AlertCircle, Building2, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Employer, EmployerSource } from "../api";

type Props = {
  employers: Employer[];
  sources: EmployerSource[];
  onSelectCompany: (employer: Employer) => void;
};

export function CompanyAttentionActions({ employers, sources, onSelectCompany }: Props) {
  const discovered = employers.filter((item) => item.status === "discovered");
  const needsReview = employers.filter((item) => item.status === "needs_review");
  const unchecked = sources.filter(
    (item) => item.status !== "verified" || item.permission_status !== "allowed",
  );
  const sourceEmployer = employers.find((item) => item.id === unchecked[0]?.employer_id);
  const actions = [
    {
      label: "Awaiting approval",
      count: discovered.length,
      icon: Building2,
      tone: "scout-status--review",
      click: () => discovered[0] && onSelectCompany(discovered[0]),
    },
    {
      label: "Flagged for review",
      count: needsReview.length,
      icon: AlertCircle,
      tone: "scout-status--rejected",
      click: () => needsReview[0] && onSelectCompany(needsReview[0]),
    },
    {
      label: "Sources to verify",
      count: unchecked.length,
      icon: ShieldAlert,
      tone: "scout-company-eyebrow",
      click: () => sourceEmployer && onSelectCompany(sourceEmployer),
    },
  ];
  return (
    <section className="grid gap-2 sm:grid-cols-3">
      {actions.map(({ label, count, icon: Icon, tone, click }) => (
        <Button
          key={label}
          type="button"
          variant="ghost"
          onClick={click}
          disabled={!count}
          className="scout-company-summary h-auto"
        >
          <span
            className={`scout-company-summary__icon ${tone}`}
          >
            <Icon className="h-4 w-4" />
          </span>
          <span className="min-w-0">
            <strong className={`scout-company-summary__count ${tone}`}>{count}</strong>
            <span className="scout-company-summary__label">{label}</span>
          </span>
        </Button>
      ))}
    </section>
  );
}
