import { useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import App from "../App";
import { supabase } from "../api-services/supabase-auth-client";
import { AdministratorLoginForm } from "./AdministratorLoginForm";

export function ScoutAuthGate() {
  const [session, setSession] = useState<Session | null>(null);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (!supabase) {
      setInitialized(true);
      return;
    }
    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setInitialized(true);
    });
    void supabase.auth.getSession().then(({ data: result }) => {
      setSession(result.session);
      setInitialized(true);
    });
    return () => data.subscription.unsubscribe();
  }, []);

  if (!initialized) {
    return <main className="grid min-h-screen place-items-center text-sm text-muted-foreground">Loading secure session…</main>;
  }
  if (!supabase) {
    return <main className="grid min-h-screen place-items-center p-6 text-center text-sm text-muted-foreground">Authentication is not configured. Set the Scout Supabase URL and publishable key in the frontend environment.</main>;
  }
  if (!session?.user.email) return <AdministratorLoginForm />;

  return (
    <App
      administratorEmail={session.user.email}
      onSignOut={() => void supabase.auth.signOut()}
    />
  );
}
