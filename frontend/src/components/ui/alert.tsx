import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const alertVariants = cva(
  "relative w-full rounded-md border px-3 py-2.5 text-sm",
  {
    variants: {
      variant: {
        default: "border-border bg-muted text-foreground",
        destructive:
          "border-border bg-[var(--danger-surface)] text-[var(--danger-text)]",
        success:
          "border-border bg-[var(--success-surface)] text-[var(--success-text)]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant, ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    />
  ),
);
Alert.displayName = "Alert";

export { Alert, alertVariants };
