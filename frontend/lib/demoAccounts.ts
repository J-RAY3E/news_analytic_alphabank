import type { Role } from "@/lib/api/types";

export interface DemoAccount {
  id: string;
  login: string;
  password: string;
  name: string;
  role: Role;
}

// Demo-only credentials (prototype). Real internet-bank auth is out of scope.
export const DEMO_ACCOUNTS: DemoAccount[] = [
  {
    id: "user-ceo",
    login: "ceo",
    password: "ceo-radar-2026",
    name: "Директор по стратегии",
    role: "CEO",
  },
  {
    id: "user-cfo",
    login: "cfo",
    password: "cfo-radar-2026",
    name: "Финансовый директор",
    role: "CFO",
  },
  {
    id: "user-treasurer",
    login: "treasurer",
    password: "treasurer-radar-2026",
    name: "Казначей",
    role: "TREASURER",
  },
  {
    id: "user-accountant",
    login: "accountant",
    password: "accountant-radar-2026",
    name: "Главный бухгалтер",
    role: "CHIEF_ACCOUNTANT",
  },
];

export function authenticate(login: string, password: string): DemoAccount | null {
  const needle = login.trim().toLowerCase();
  return (
    DEMO_ACCOUNTS.find(
      (account) => account.login === needle && account.password === password
    ) ?? null
  );
}

export function accountById(id: string | null): DemoAccount | null {
  if (!id) return null;
  return DEMO_ACCOUNTS.find((account) => account.id === id) ?? null;
}
