import { useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import type { AnalysisReport, Issue } from "../types";

const severityStyles = {
  High: "bg-red-400/10 text-red-300 ring-red-400/30",
  Medium: "bg-orange-400/10 text-orange-300 ring-orange-400/30",
  Low: "bg-emerald-400/10 text-emerald-300 ring-emerald-400/30",
};

function IssueCard({ issue }: { issue: Issue }) {
  const [copied, setCopied] = useState(false);
  async function copy() {
    await navigator.clipboard.writeText(issue.fix_command);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }
  return (
    <article className="panel p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs text-slate-500">{issue.resource_name}</p>
          <p className="mt-1 break-all font-mono text-xs text-slate-600">{issue.resource_id}</p>
          <h3 className="mt-1 font-semibold">{issue.issue_type}</h3>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs ring-1 ${severityStyles[issue.severity]}`}>{issue.severity}</span>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-400">{issue.description}</p>
      <p className="mt-3 text-sm font-medium text-signal">${Number(issue.estimated_savings).toFixed(2)} estimated monthly savings</p>
      <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/80 p-4">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-wider text-slate-500">Native CLI remediation</p>
          <button className="text-xs text-signal hover:text-cyan-200" onClick={copy}>{copied ? "Copied" : "Copy command"}</button>
        </div>
        <code className="mt-3 block overflow-x-auto whitespace-pre text-xs text-slate-300">{issue.fix_command}</code>
      </div>
    </article>
  );
}

export function Report() {
  const { state } = useLocation();
  const report = (state as { report?: AnalysisReport } | null)?.report;
  if (!report) return <Navigate to="/" replace />;
  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-xs uppercase tracking-[0.24em] text-signal">Optimization intelligence</p>
      <h1 className="mt-3 text-4xl font-semibold">Cost analysis report</h1>
      <p className="mt-3 max-w-3xl text-slate-400">{report.summary}</p>
      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="panel p-5"><p className="text-xs text-slate-500">Cloud provider</p><p className="mt-2 text-3xl font-semibold uppercase text-violet">{report.provider ?? "—"}</p></div>
        <div className="panel p-5"><p className="text-xs text-slate-500">Resources scanned</p><p className="mt-2 text-3xl font-semibold">{report.resources_scanned ?? "—"}</p></div>
        <div className="panel p-5"><p className="text-xs text-slate-500">Optimization issues</p><p className="mt-2 text-3xl font-semibold">{report.issues.length}</p></div>
        <div className="panel p-5"><p className="text-xs text-slate-500">Monthly savings</p><p className="mt-2 text-3xl font-semibold text-signal">${Number(report.total_estimated_monthly_savings).toFixed(2)}</p></div>
      </section>
      <section className="mt-10">
        <h2 className="text-xl font-semibold">Prioritized recommendations</h2>
        <div className="mt-4 grid gap-4">{report.issues.length ? report.issues.map((issue) => <IssueCard key={`${issue.resource_id}-${issue.issue_type}`} issue={issue} />) : <div className="panel p-6 text-slate-400">No actionable savings opportunities were identified.</div>}</div>
      </section>
    </main>
  );
}
