import type {
  ApiErrorShape,
  CompanySummary,
  EventDetailResponse,
  FeedbackRequest,
  FeedbackResponse,
  FeedResponse,
  IngestRequest,
  IngestResponse,
  InsightRequest,
  InsightResponse,
  Role,
  TraceResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

export class ApiError extends Error {
  code: string;
  requestId: string | null;

  constructor(code: string, message: string, requestId: string | null = null) {
    super(message);
    this.code = code;
    this.requestId = requestId;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError("network_error", "Сервер недоступен. Проверьте подключение.");
  }

  const requestId = res.headers.get("x-request-id");

  if (!res.ok) {
    let message = `Ошибка запроса (${res.status})`;
    let code = `http_${res.status}`;
    try {
      const body = (await res.json()) as ApiErrorShape;
      if (body?.error) {
        message = body.error.message;
        code = body.error.code;
      }
    } catch {
      // keep defaults
    }
    throw new ApiError(code, message, requestId);
  }

  return (await res.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  listCompanies: (params: { q?: string; target_only?: boolean; limit?: number } = {}) => {
    const sp = new URLSearchParams();
    if (params.q) sp.set("q", params.q);
    if (params.target_only) sp.set("target_only", "true");
    sp.set("limit", String(params.limit ?? 50));
    return request<{ items: CompanySummary[]; total: number }>(`/companies?${sp}`);
  },

  getCompany: (companyId: string) =>
    request<{ items: CompanySummary[] }>(`/companies/${encodeURIComponent(companyId)}`),

  getFeed: (companyId: string, role: Role, limit = 10) => {
    const sp = new URLSearchParams({ company_id: companyId, role, limit: String(limit) });
    return request<FeedResponse>(`/feed?${sp}`);
  },

  getEvent: (eventId: string) =>
    request<EventDetailResponse>(`/events/${encodeURIComponent(eventId)}`),

  ingest: (body: IngestRequest) =>
    request<IngestResponse>("/ingest", { method: "POST", body: JSON.stringify(body) }),

  createInsight: (body: InsightRequest) =>
    request<InsightResponse>("/insight", { method: "POST", body: JSON.stringify(body) }),

  getTrace: (traceId: string) =>
    request<TraceResponse>(`/trace/${encodeURIComponent(traceId)}`),

  submitFeedback: (body: FeedbackRequest) =>
    request<FeedbackResponse>("/feedback", { method: "POST", body: JSON.stringify(body) }),
};
