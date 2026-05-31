import { useEffect, useState } from "react";
import { progressSocketUrl } from "../services/api";
import type { AnalysisReport, ProgressEvent } from "../types";

const steps = [
  "Connecting",
  "Scanning",
  "Normalizing",
  "AI analysis",
  "Persisting",
  "Complete",
];

export function ProgressTracker({
  socketPath,
  onComplete,
  onFailure,
}: {
  socketPath: string;
  onComplete: (report: AnalysisReport) => void;
  onFailure: (message: string) => void;
}) {
  const [event, setEvent] = useState<ProgressEvent | null>(null);

  useEffect(() => {
    const socket = new WebSocket(progressSocketUrl(socketPath));
    let disposed = false;
    socket.onmessage = ({ data }) => {
      if (disposed) return;
      const next = JSON.parse(data) as ProgressEvent;
      setEvent(next);
      if (next.status === "completed" && next.result) onComplete(next.result);
      if (next.status === "failed") onFailure(next.message);
    };
    socket.onerror = () => {
      if (!disposed) onFailure("The live progress channel could not be opened.");
    };
    return () => {
      disposed = true;
      socket.close();
    };
  }, [socketPath, onComplete, onFailure]);

  const progress = event?.progress ?? 0;
  return (
    <section className="panel mt-8 p-6" aria-live="polite">
      <div className="mb-4 flex justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-signal">Live pipeline</p>
          <h2 className="mt-2 text-lg font-semibold">Analysis in progress</h2>
        </div>
        <span className="font-mono text-2xl text-signal">{progress}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div className="h-full rounded-full bg-signal transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>
      <div className="mt-6 grid gap-2 sm:grid-cols-6">
        {steps.map((step, index) => {
          const threshold = [5, 20, 45, 60, 85, 100][index];
          return <div key={step} className={`text-xs ${progress >= threshold ? "text-signal" : "text-slate-600"}`}>{step}</div>;
        })}
      </div>
      <p className={`mt-5 text-sm ${event?.status === "failed" ? "text-red-300" : "text-slate-300"}`}>
        {event?.message ?? "Opening secure progress channel..."}
      </p>
    </section>
  );
}
