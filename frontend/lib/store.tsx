"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { Role } from "@/lib/api/types";
import { accountById } from "@/lib/demoAccounts";

export interface DemoUser {
  id: string;
  name: string;
  role: Role;
}

interface AppState {
  user: DemoUser | null;
  hydrated: boolean;
  setUserId: (id: string) => void;
  companyId: string | null;
  setCompanyId: (id: string) => void;
  role: Role;
  setRole: (role: Role) => void;
}

const STORAGE_KEY = "alfa_radar_state_v2";

const AppStateContext = createContext<AppState | null>(null);

interface Persisted {
  userId: string | null;
  companyId: string | null;
  role: Role;
}

function resolveUser(id: string | null): DemoUser | null {
  const account = accountById(id);
  return account ? { id: account.id, name: account.name, role: account.role } : null;
}

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<DemoUser | null>(null);
  const [companyId, setCompanyIdState] = useState<string | null>(null);
  const [role, setRoleState] = useState<Role>("CEO");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Persisted;
        setUser(resolveUser(parsed.userId));
        if (parsed.companyId) setCompanyIdState(parsed.companyId);
        if (parsed.role) setRoleState(parsed.role);
      }
    } catch {
      // corrupted storage: start fresh
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    const value: Persisted = { userId: user?.id ?? null, companyId, role };
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    } catch {
      // storage unavailable
    }
  }, [user, companyId, role, hydrated]);

  const setUserId = useCallback((id: string) => {
    setUser(resolveUser(id));
  }, []);

  const value = useMemo<AppState>(
    () => ({
      user,
      hydrated,
      setUserId,
      companyId,
      setCompanyId: setCompanyIdState,
      role,
      setRole: setRoleState,
    }),
    [user, hydrated, setUserId, companyId, role]
  );

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState(): AppState {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppStateProvider");
  return ctx;
}
