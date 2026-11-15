import { useState, type FormEvent } from "react";
import { LockKeyhole } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { supabase } from "../api-services/supabase-auth-client";

export function AdministratorLoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

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
            <Input id="admin-email" type="email" autoComplete="username" required
              value={email} onChange={event => setEmail(event.target.value)} />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="admin-password" className="text-sm font-medium">Password</label>
            <Input id="admin-password" type="password" autoComplete="current-password" required
              value={password} onChange={event => setPassword(event.target.value)} />
          </div>
          {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
          <Button className="w-full" type="submit" disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </Button>
        </form>
        <p className="mt-4 text-center text-xs text-muted-foreground">
          Access is restricted to the configured administrator.
        </p>
      </section>
    </main>
  );
}
