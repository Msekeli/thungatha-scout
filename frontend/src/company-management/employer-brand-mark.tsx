import { Building2 } from "lucide-react";

type EmployerBrandMarkProps = {
  name: string;
  logoUrl?: string | null;
  className: string;
  logoClassName: string;
};

function getInitials(name: string): string {
  const words = name.trim().split(/\s+/).filter(Boolean).slice(0, 2);
  return words.map((word) => Array.from(word)[0] ?? "").join("").toUpperCase();
}

export function EmployerBrandMark({
  name,
  logoUrl,
  className,
  logoClassName,
}: EmployerBrandMarkProps) {
  const initials = getInitials(name);
  return (
    <span className={className} role="img" aria-label={name + " branding"}>
      <span
        aria-hidden="true"
        className="grid h-full w-full place-items-center text-xs font-bold tracking-wide"
      >
        {initials || <Building2 className="h-5 w-5" />}
      </span>
      {logoUrl && (
        <img
          src={logoUrl}
          alt=""
          className={logoClassName}
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
      )}
    </span>
  );
}
