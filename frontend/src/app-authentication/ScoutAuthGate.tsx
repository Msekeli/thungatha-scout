import { useEffect, useState, type FormEvent } from "react";
import type { Session } from "@supabase/supabase-js";
import { LockKeyhole } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import App from "../App";
import { supabase } from "../api-services/supabase-auth-client";

export function ScoutAuthGate() {
  const [session, setSession] = useState<Session | null>(null);
  const [initialized, setInitialized] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

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

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!supabase) return;
    setSubmitting(true);
    setError("");
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    if (signInError) setError("Sign-in failed. Check your email and password.");
    setSubmitting(false);
  }

  if (!initialized) {
    return <main className="grid min-h-screen place-items-center text-sm text-muted-foreground">Loading secure session…</main>;
  }

  if (!supabase) {
    return <main className="grid min-h-screen place-items-center p-6 text-center text-sm text-muted-foreground">Authentication is not configured. Add the Scout Supabase URL and publishable key to the frontend environment.</main>;
  }

  if (session?.user.email) {
    return (
      <App
        administratorEmail={session.user.email}
        onSignOut={() => void supabase.auth.signOut()}
      />
    );
  }

  return (
    <main className="grid min-h-screen place-items-center bg-background px-4 py-8">
      <section className="w-full max-w-sm rounded-xl border border-border bg-card p-6 text-card-foreground shadow-lg">
        <div className="mb-6 flex flex-col items-center text-center">
          <img src="/branding/logo.svg" alt="Thungatha Scout" className="mb-6 h-12 w-auto" />
          <div className="mb-3 grid h-11 w-11 place-items-center rounded-full bg-accent text-primary">
            <LockKeyhole className="h-5 w-5" />
          </div>
          <h1 className="text-xl font-semibold">Administrator sign in</h1>
          <p className="mt-1 text-sm text-muted-foreground">Sign in with your authorised Scout account.</p>
        </div>
        <form className="space-y-4" onSubmit={signIn}>
          <div className="space-y-1.5">
            <label htmlFor="admin-email" className="text-sm font-medium">Email</label>
            <Input id="admin-email" type="email" autoComplete="username" required value={email} onChange={event => setEmail(event.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="admin-password" className="text-sm font-medium">Password</label>
            <Input id="admin-password" type="password" autoComplete="current-password" required value={password} onChange={event => setPassword(event.target.value)} />
          </div>
          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
          <Button className="w-full" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </Button>
        </form>
        <p className="mt-4 text-center text-xs text-muted-foreground">Access is restricted to the configured administrator.</p>
      </section>
    </main>
  );
}
