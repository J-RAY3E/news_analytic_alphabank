import { api, USE_MOCKS } from "@/lib/api/client";
import type {
  Budget,
  ChatResponse,
  CompanySummary,
  EventDetailResponse,
  FeedbackRequest,
  FeedbackResponse,
  FeedResponse,
  IngestRequest,
  IngestResponse,
  InsightListResponse,
  InsightRequest,
  InsightResponse,
  Metrics,
  Role,
  SourceInfo,
  TraceResponse,
} from "@/lib/api/types";
import { buildMockFeed, buildMockInsight, getMockEvent, MOCK_COMPANIES, MOCK_SOURCES, MOCK_TRACE } from "./data";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function mockEventDetail(eventId: string): EventDetailResponse | null {
  const event = getMockEvent(eventId);
  return event ? { event } : null;
}

function mockIngest(body: IngestRequest): IngestResponse {
  const title = body.title?.trim() || (body.text ? body.text.slice(0, 80) : "Новая проверенная новость");
  const text = body.text ?? "";
  const isUrl = Boolean(body.url);
  return {
    event: {
      event_id: `news:demo-${Date.now()}`,
      title,
      summary: text.slice(0, 300) || "Содержание получено по ссылке и нормализовано.",
      event_type: "REGULATION",
      sectors: ["Все отрасли"],
      regions: ["Россия"],
      countries: ["Россия"],
      macro_factors: ["REGULATION"],
      entities: [],
      figures: [],
      sentiment: "NEUTRAL",
      risk_opportunity: "NEUTRAL",
      is_speculation: false,
      noise_score: 0.1,
      confidence: 0.6,
      source: {
        source_id: `news:demo-${Date.now()}`,
        name: isUrl ? "Пользовательская ссылка" : "Текст пользователя",
        url: body.url ?? null,
        published_at: new Date().toISOString(),
        language: "ru",
      },
      ingested_at: new Date().toISOString(),
    },
    duplicate_of: null,
  };
}

export const dataApi = {
  listCompanies: async (): Promise<{ items: CompanySummary[]; total: number }> => {
    if (!USE_MOCKS) return api.listCompanies();
    await delay(250);
    return { items: MOCK_COMPANIES, total: MOCK_COMPANIES.length };
  },

  getCompany: async (companyId: string): Promise<{ items: CompanySummary[] }> => {
    if (!USE_MOCKS) return api.getCompany(companyId);
    await delay(150);
    const items = MOCK_COMPANIES.filter((c) => c.company_id === companyId);
    if (!items.length) {
      throw new Error("Клиент не найден");
    }
    return { items };
  },

  getFeed: async (companyId: string, role: Role, limit = 10): Promise<FeedResponse> => {
    if (!USE_MOCKS) return api.getFeed(companyId, role, limit);
    await delay(500);
    const company = MOCK_COMPANIES.find((c) => c.company_id === companyId);
    if (!company) throw new Error("Клиент не найден");
    return {
      company,
      role,
      items: buildMockFeed(company, role).slice(0, limit),
      scoring_config_version: "scoring.yaml@2026-07-25",
    };
  },

  getEvent: async (eventId: string): Promise<EventDetailResponse> => {
    if (!USE_MOCKS) return api.getEvent(eventId);
    await delay(200);
    const detail = mockEventDetail(eventId);
    if (!detail) throw new Error("Событие не найдено");
    return detail;
  },

  ingest: async (body: IngestRequest): Promise<IngestResponse> => {
    if (!USE_MOCKS) return api.ingest(body);
    await delay(1800);
    return mockIngest(body);
  },

  createInsight: async (body: InsightRequest): Promise<InsightResponse> => {
    if (!USE_MOCKS) return api.createInsight(body);
    await delay(2200);
    const company = MOCK_COMPANIES.find((c) => c.company_id === body.company_id);
    if (!company) throw new Error("Клиент не найден");
    return buildMockInsight(company, body.event_id, body.role ?? "CEO");
  },

  getInsight: async (insightId: string): Promise<InsightResponse> => {
    if (!USE_MOCKS) return api.getInsight(insightId);
    await delay(200);
    return buildMockInsight(MOCK_COMPANIES[0], "news:demo", "CEO");
  },

  listInsights: async (
    params: { company_id?: string; role?: Role; limit?: number } = {}
  ): Promise<InsightListResponse> => {
    if (!USE_MOCKS) return api.listInsights(params);
    await delay(200);
    return { items: [], total: 0 };
  },

  getTrace: async (traceId: string): Promise<TraceResponse> => {
    if (!USE_MOCKS) return api.getTrace(traceId);
    await delay(200);
    return {
      trace_id: traceId,
      events: MOCK_TRACE.filter((e) => e.trace_id === traceId) as unknown as Record<string, unknown>[],
    };
  },

  submitFeedback: async (body: FeedbackRequest): Promise<FeedbackResponse> => {
    if (!USE_MOCKS) return api.submitFeedback(body);
    await delay(300);
    return { stored: true, feedback_id: `fb_${Date.now()}` };
  },

  getBudget: async (): Promise<Budget> => {
    if (!USE_MOCKS) return api.getBudget();
    await delay(150);
    return {
      day: new Date().toISOString().slice(0, 10),
      spent_rub: 214.6,
      budget_rub: 500,
      remaining_rub: 285.4,
      model: "GLM-5.3-Flash",
      cache_hits: 12,
    };
  },

  getMetrics: async (): Promise<Metrics> => {
    if (!USE_MOCKS) return api.getMetrics();
    await delay(150);
    return {
      generated_at: new Date().toISOString(),
      events_total: 0,
      insights_total: 0,
      feedback_total: 0,
      thumbs_up_ratio: null,
      source_coverage: 0,
      avg_cost_rub: null,
      avg_latency_ms: null,
      llm_spent_today_rub: 0,
      llm_budget_rub: 500,
    };
  },

  getSource: async (sourceId: string): Promise<SourceInfo> => {
    if (!USE_MOCKS) return api.getSource(sourceId);
    await delay(150);
    const source = MOCK_SOURCES[sourceId];
    return {
      source_id: sourceId,
      kind: source ? "news" : "unknown",
      name: source?.name ?? "Источник",
      url: source?.url ?? null,
      page: source?.page ?? null,
      snippet: null,
    };
  },

  chat: async (insightId: string, question: string): Promise<ChatResponse> => {
    if (!USE_MOCKS) return api.chat(insightId, question);
    await delay(500);
    return {
      text: `Демо-ответ на вопрос: «${question}». Для реального анализа отключите моки.`,
      claim: null,
    };
  },
};
