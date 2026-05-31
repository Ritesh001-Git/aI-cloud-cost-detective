import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Navbar() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm transition ${isActive ? "text-signal" : "text-slate-400 hover:text-white"}`;

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <NavLink to="/" className="font-semibold tracking-wide text-white">
          <span className="mr-2 text-signal">◆</span>Cloud Cost Detective
        </NavLink>
        <div className="flex items-center gap-6">
          <NavLink to="/" className={linkClass}>Dashboard</NavLink>
          <NavLink to="/history" className={linkClass}>History</NavLink>
          <button
            className="rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 hover:border-slate-500"
            onClick={() => { logout(); navigate("/login"); }}
          >
            Sign out
          </button>
        </div>
      </nav>
    </header>
  );
}
