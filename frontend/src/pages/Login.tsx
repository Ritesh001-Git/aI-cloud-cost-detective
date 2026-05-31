import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to sign in.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <form onSubmit={submit} className="panel w-full max-w-md p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-signal">Secure workspace</p>
        <h1 className="mt-3 text-3xl font-semibold">Welcome back</h1>
        <p className="mt-2 text-sm text-slate-400">Sign in to inspect your multi-cloud efficiency ledger.</p>
        <label className="mt-8 block text-sm text-slate-300">
          Email
          <input className="field mt-2" type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label className="mt-4 block text-sm text-slate-300">
          Password
          <input className="field mt-2" type="password" required minLength={8} autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error && <p className="mt-4 text-sm text-red-300">{error}</p>}
        <button className="button-primary mt-6 w-full" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
        <p className="mt-6 text-center text-sm text-slate-400">New here? <Link className="text-signal hover:text-cyan-200" to="/signup">Create an account</Link></p>
      </form>
    </main>
  );
}
