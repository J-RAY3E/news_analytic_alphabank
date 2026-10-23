import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

const NBSP_THIN = "\u202F";

export function formatRub(value: number): string {
  const billions = value / 1_000_000_000;
  if (billions >= 1) {
    return `${formatNumber(billions)}${NBSP_THIN}млрд${NBSP_THIN}руб.`;
  }
  return `${formatNumber(value)}${NBSP_THIN}руб.`;
}

export function formatNumber(value: number, digits = 1): string {
  const fixed = value.toFixed(digits);
  const [intPart, decPart] = fixed.split(".");
  const withSep = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP_THIN);
  if (!decPart || decPart === "0".repeat(decPart.length)) {
    return withSep;
  }
  return `${withSep},${decPart}`;
}

export function formatScore(value: number): string {
  return formatNumber(value, 2);
}

export function formatPercent(value: number, digits = 1): string {
  return `${formatNumber(value, digits)}%`;
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString("ru-RU", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}

export function pluralRu(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few;
  return many;
}
