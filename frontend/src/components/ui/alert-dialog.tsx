import * as DialogPrimitive from "@radix-ui/react-dialog";
import type { ComponentPropsWithoutRef } from "react";

export const AlertDialog = DialogPrimitive.Root;
export const AlertDialogPortal = DialogPrimitive.Portal;
export const AlertDialogTrigger = DialogPrimitive.Trigger;
export const AlertDialogCancel = DialogPrimitive.Close;

export function AlertDialogOverlay() {
  return (
    <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out" />
  );
}

export function AlertDialogContent(
  props: ComponentPropsWithoutRef<typeof DialogPrimitive.Content>,
) {
  return (
    <DialogPrimitive.Portal>
      <AlertDialogOverlay />
      <DialogPrimitive.Content
        role="alertdialog"
        aria-describedby={props["aria-describedby"]}
        className="fixed left-1/2 top-1/2 z-50 grid w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl border border-border bg-card p-6 text-card-foreground shadow-xl outline-none"
        {...props}
      />
    </DialogPrimitive.Portal>
  );
}

export function AlertDialogHeader(props: ComponentPropsWithoutRef<"div">) {
  return <div className="flex flex-col gap-2 text-left" {...props} />;
}

export const AlertDialogTitle = DialogPrimitive.Title;
export const AlertDialogDescription = DialogPrimitive.Description;

export function AlertDialogFooter(props: ComponentPropsWithoutRef<"div">) {
  return <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end" {...props} />;
}

export const AlertDialogAction = DialogPrimitive.Close;
