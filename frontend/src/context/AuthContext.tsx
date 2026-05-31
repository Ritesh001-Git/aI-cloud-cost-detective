import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { authenticate, getToken, setToken } from "../services/api";

interface AuthContextValue {
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, updateToken] = useState(getToken());

  const persist = (value: string | null) => {
    setToken(value);
    updateToken(value);
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      login: async (email, password) => persist((await authenticate("login", email, password)).access_token),
      signup: async (email, password) => persist((await authenticate("signup", email, password)).access_token),
      logout: () => persist(null),
    }),
    [token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider.");
  return context;
}
