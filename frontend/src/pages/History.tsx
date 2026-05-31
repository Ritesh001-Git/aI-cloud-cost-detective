import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getHistory } from "../services/api";
import type { HistoryItem } from "../types";

export function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getHistory().then(({ analyses }) => setItems(analyses)).catch((reason: Error) => setError(reason.message));
  }, []);

  function open(item: HistoryItem) {
    navigate("/report", {
      state: {
        report: {
          ...item.analysis_result,
          resources_scanned: item.resources_scanned,
          provider: item.provider,
          target_scope: item.target_scope,
        },
      },
    });
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-xs uppercase tracking-[0.24em] text-violet">Persistent ledger</p>
      <h1 className="mt-3 text-4xl font-semibold">Analysis history</h1>
      <p className="mt-3 text-slate-400">Review completed diagnostics across each provider boundary.</p>
      {error && <p className="mt-6 text-sm text-red-300">{error}</p>}
      <div className="panel mt-8 overflow-hidden">
        <div className="hidden grid-cols-6 gap-4 border-b border-slate-800 px-5 py-3 text-xs uppercase tracking-wider text-slate-500 md:grid">
          <span>Provider</span><span>Scope</span><span>Date</span><span>Resources</span><span>Issues</span><span>Savings</span>
        </div>
        {items.map((item) => (
          <button key={item.id} className="grid w-full gap-2 border-b border-slate-800/80 px-5 py-4 text-left transition last:border-0 hover:bg-slate-800/40 md:grid-cols-6 md:gap-4" onClick={() => open(item)}>
            <span className="text-sm uppercase text-signal">{item.provider}</span>
            <span className="truncate text-sm text-slate-300">{item.target_scope}</span>
            <span className="text-sm text-slate-500">{new Date(item.created_at).toLocaleString()}</span>
            <span className="text-sm text-slate-300">{item.resources_scanned}</span>
            <span className="text-sm text-slate-300">{item.issues_found}</span>
            <span className="text-sm font-medium text-signal">${Number(item.estimated_savings).toFixed(2)}</span>
          </button>
        ))}
        {!items.length && !error && <p className="px-5 py-8 text-sm text-slate-500">No completed analyses yet.</p>}
      </div>
    </main>
  );
}
