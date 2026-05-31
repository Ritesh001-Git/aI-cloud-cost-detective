import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Signup() {
  const { signup } = useAuth();
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
      await signup(email, password);
      navigate("/");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create your account.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <form onSubmit={submit} className="panel w-full max-w-md p-8">
        <p className="text-xs uppercase tracking-[0.24em] text-violet">New operator</p>
        <h1 className="mt-3 text-3xl font-semibold">Create your account</h1>
        <p className="mt-2 text-sm text-slate-400">Start a private cost-optimization workspace.</p>
        <label className="mt-8 block text-sm text-slate-300">
          Email
          <input className="field mt-2" type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label className="mt-4 block text-sm text-slate-300">
          Password
          <input className="field mt-2" type="password" required minLength={8} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error && <p className="mt-4 text-sm text-red-300">{error}</p>}
        <button className="button-primary mt-6 w-full" disabled={busy}>{busy ? "Creating account..." : "Create account"}</button>
        <p className="mt-6 text-center text-sm text-slate-400">Already registered? <Link className="text-signal hover:text-cyan-200" to="/login">Sign in</Link></p>
      </form>
    </main>
  );
}
