import type { FC } from "react";

export const AppShellHeader: FC = () => {
  return (
    <header className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg font-black tracking-tight text-cyan-800 shadow-sm bg-white">
          S
        </span>
        <div>
          <p className="text-[10px] font-extrabold uppercase tracking-widest text-cyan-200">
            THUNGATHA / OPERATIONS
          </p>
          <h1 className="text-xl font-extrabold tracking-tight text-white">Scout</h1>
        </div>
      </div>
      <span className="rounded-full bg-white/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-cyan-100 backdrop-blur-sm">
        PRIVATE ADMIN
      </span>
    </header>
  );
};
