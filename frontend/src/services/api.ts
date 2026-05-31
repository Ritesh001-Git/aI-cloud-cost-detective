import type { AnalysisReport, HistoryItem, Provider, Scope } from "../types";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ??
  `${window.location.protocol}//${window.location.hostname}:8000`;
const TOKEN_KEY = "cloud-cost-detective-token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail ?? "Request failed.");
  return payload;
}

export async function authenticate(mode: "login" | "signup", email: string, password: string) {
  return request<{ access_token: string }>(`/api/auth/${mode}`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getScopes(provider: Provider) {
  return request<{ scopes: Scope[] }>(`/api/accounts-or-groups?provider=${provider}`);
}

export async function startAnalysis(provider: Provider, target_scope: string) {
  return request<{ analysis_id: string; websocket_url: string }>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ provider, target_scope }),
  });
}

export async function getHistory() {
  return request<{ analyses: HistoryItem[] }>("/api/history");
}

export function progressSocketUrl(path: string) {
  const token = encodeURIComponent(getToken() ?? "");
  return `${API_BASE.replace(/^http/, "ws")}${path}?token=${token}`;
}

export type { AnalysisReport };
