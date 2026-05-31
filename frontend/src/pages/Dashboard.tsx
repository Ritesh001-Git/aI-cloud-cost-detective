import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ProgressTracker } from "../components/ProgressTracker";
import { getScopes, startAnalysis } from "../services/api";
import type { AnalysisReport, Provider, Scope } from "../types";

const providers: { id: Provider; name: string; mark: string; description: string }[] = [
  { id: "aws", name: "AWS", mark: "AWS", description: "Regions and tagged resources" },
  { id: "azure", name: "Azure", mark: "AZ", description: "Resource groups and assets" },
  { id: "gcp", name: "Google Cloud", mark: "GCP", description: "Projects and cloud assets" },
];

export function Dashboard() {
  const navigate = useNavigate();
  const [provider, setProvider] = useState<Provider>("aws");
  const [scopes, setScopes] = useState<Scope[]>([]);
  const [scope, setScope] = useState("");
  const [error, setError] = useState("");
  const [loadingScopes, setLoadingScopes] = useState(false);
  const [running, setRunning] = useState(false);
  const [socketPath, setSocketPath] = useState("");

  useEffect(() => {
    setLoadingScopes(true);
    setError("");
    setScope("");
    getScopes(provider)
      .then(({ scopes: next }) => setScopes(next))
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoadingScopes(false));
  }, [provider]);

  const complete = useCallback((report: AnalysisReport) => {
    navigate("/report", { state: { report } });
  }, [navigate]);

  const fail = useCallback((message: string) => {
    setError(message);
    setRunning(false);
    setSocketPath("");
  }, []);

  async function run() {
    if (!scope) return;
    setError("");
    setRunning(true);
    try {
      const result = await startAnalysis(provider, scope);
      setSocketPath(result.websocket_url);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to start analysis.");
      setRunning(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-xs uppercase tracking-[0.24em] text-signal">Unified FinOps command center</p>
      <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight">Find the cloud spend that is quietly doing nothing.</h1>
      <p className="mt-4 max-w-2xl text-slate-400">Select a provider boundary, inspect its live inventory, and generate operator-ready remediation commands.</p>

      <section className="mt-10 grid gap-4 md:grid-cols-3">
        {providers.map((item) => (
          <button
            key={item.id}
            className={`panel p-5 text-left transition ${provider === item.id ? "border-signal ring-2 ring-signal/20" : "hover:border-slate-600"}`}
            onClick={() => setProvider(item.id)}
          >
            <span className="inline-flex h-11 min-w-11 items-center justify-center rounded-lg bg-slate-900 px-2 font-mono text-xs text-signal">{item.mark}</span>
            <h2 className="mt-5 font-semibold">{item.name}</h2>
            <p className="mt-1 text-sm text-slate-500">{item.description}</p>
          </button>
        ))}
      </section>

      <section className="panel mt-6 flex flex-col gap-4 p-6 md:flex-row md:items-end">
        <label className="flex-1 text-sm text-slate-300">
          Target scope
          <select className="field mt-2" value={scope} disabled={loadingScopes || running} onChange={(event) => setScope(event.target.value)}>
            <option value="">{loadingScopes ? "Loading scopes..." : "Select a scope"}</option>
            {scopes.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
        </label>
        <button className="button-primary md:min-w-52" disabled={!scope || running} onClick={run}>{running ? "Pipeline running..." : "Run Scan & Analyze"}</button>
      </section>
      {error && <p className="mt-4 text-sm text-red-300">{error}</p>}
      {socketPath && <ProgressTracker socketPath={socketPath} onComplete={complete} onFailure={fail} />}
    </main>
  );
}
