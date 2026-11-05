import { AlertCircle, BadgeCheck, Building2, ShieldAlert } from "lucide-react";
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
      tone: "text-amber-300",
      click: () => discovered[0] && onSelectCompany(discovered[0]),
    },
    {
      label: "Flagged for review",
      count: needsReview.length,
      icon: AlertCircle,
      tone: "text-rose-300",
      click: () => needsReview[0] && onSelectCompany(needsReview[0]),
    },
    {
      label: "Sources to verify",
      count: unchecked.length,
      icon: ShieldAlert,
      tone: "text-cyan-300",
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
          className="h-auto justify-start gap-3 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-3 text-left shadow-md shadow-black/10 hover:border-slate-600 hover:bg-slate-800"
        >
          <span
            className={`grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-white/5 ${tone}`}
          >
            <Icon className="h-4 w-4" />
          </span>
          <span className="min-w-0">
            <strong className={`block text-lg font-bold leading-5 ${tone}`}>{count}</strong>
            <span className="text-xs text-slate-400">{label}</span>
          </span>
        </Button>
      ))}
    </section>
  );
}
