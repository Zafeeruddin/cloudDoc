import { createContext, useContext, useMemo, useState } from "react";

const STORAGE_KEY = "docops.auth";
const DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001";
const DEFAULT_EMAIL = "demo@docops.local";
const DEFAULT_NAME = "Demo User";

function buildToken(userId, email, name) {
  return `docops:${userId}:${email}:${name}`;
}

const AuthContext = createContext(null);

function loadInitialState() {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return {
      userId: DEFAULT_USER_ID,
      email: DEFAULT_EMAIL,
      name: DEFAULT_NAME,
      token: buildToken(DEFAULT_USER_ID, DEFAULT_EMAIL, DEFAULT_NAME),
      isAuthenticated: false,
    };
  }

  const parsed = JSON.parse(raw);
  return {
    ...parsed,
    name: parsed?.name || DEFAULT_NAME,
    isAuthenticated: Boolean(parsed?.token),
  };
}

export function AuthProvider({ children }) {
  const [state, setState] = useState(loadInitialState);

  const value = useMemo(
    () => ({
      ...state,
      login(nextState) {
        const payload = {
          userId: nextState.userId,
          email: nextState.email,
          name: nextState.name,
          token: nextState.token || buildToken(nextState.userId, nextState.email, nextState.name),
          isAuthenticated: true,
        };
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
        setState(payload);
      },
      logout() {
        window.localStorage.removeItem(STORAGE_KEY);
        setState({
          userId: DEFAULT_USER_ID,
          email: DEFAULT_EMAIL,
          name: DEFAULT_NAME,
          token: buildToken(DEFAULT_USER_ID, DEFAULT_EMAIL, DEFAULT_NAME),
          isAuthenticated: false,
        });
      },
    }),
    [state],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
