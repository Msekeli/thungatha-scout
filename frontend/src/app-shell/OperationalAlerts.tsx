import type { FC } from "react";

type OperationalAlertsProps = {
  error?: string | null;
  notice?: string | null;
};

export const OperationalAlerts: FC<OperationalAlertsProps> = ({ error, notice }) => {
  return (
    <>
      {error && (
        <div className="alert error" role="alert">
          {error}
        </div>
      )}
      {notice && (
        <div className="alert success" role="status">
          {notice}
        </div>
      )}
    </>
  );
};
