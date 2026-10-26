export type Role = "CEO" | "CFO" | "TREASURER" | "CHIEF_ACCOUNTANT" | "OTHER";

export type ClaimType = "FACT" | "BANK_VIEW" | "AI_INFERENCE" | "HYPOTHESIS";

export type Impact = "LOW" | "MEDIUM" | "HIGH";

export type EventType =
  | "MONETARY_POLICY"
  | "FX"
  | "REGULATION"
  | "SANCTIONS"
  | "LOGISTICS"
  | "COMMODITIES"
  | "DEMAND"
  | "COMPETITION"
  | "TAX"
  | "LABOR"
  | "TECHNOLOGY"
  | "OTHER";

export type MacroFactor =
  | "KEY_RATE"
  | "INFLATION"
  | "FX_RATE"
  | "BOND_YIELD"
  | "COMMODITY_PRICE"
  | "DEMAND"
  | "SUPPLY_CHAIN"
  | "REGULATION"
  | "TAX"
  | "SANCTIONS"
  | "LABOR_COST"
  | "CREDIT_ACCESS";

export type Sentiment = "POSITIVE" | "NEUTRAL" | "NEGATIVE" | "MIXED";

export type RiskOpportunity = "RISK" | "OPPORTUNITY" | "BOTH" | "NEUTRAL";

export interface Figure {
  label: string;
  value: number | string;
  unit?: string | null;
}

export interface SourceRef {
  source_id: string;
  name: string;
  url?: string | null;
  published_at?: string | null;
  page?: number | null;
  language?: string;
}

export interface CompanySummary {
  company_id: string;
  display_name: string;
  okved_code: string;
  okved_name: string;
  okved_division?: string | null;
  okved_section?: string | null;
  industry_label: string;
  region: string;
  city: string;
  revenue_rub: number;
  revenue_band: string;
  employees_band: string;
  client_type: string;
  product_flags: string[];
  is_exporter: boolean;
  fts_countries: string[];
  group_id?: string | null;
  group_size: number;
  group_revenue_rub?: number;
}

export interface RelevanceFactor {
  name: string;
  value: number;
  weight: number;
  contribution: number;
  explanation: string;
}

export interface FeedEventCard {
  event_id: string;
  title: string;
  summary: string;
  event_type: EventType;
  sectors: string[];
  regions: string[];
  countries: string[];
  macro_factors: MacroFactor[];
  sentiment: Sentiment;
  risk_opportunity: RiskOpportunity;
  published_at?: string | null;
  source_name: string;
  source_url?: string | null;
}

export interface FeedItem {
  event: FeedEventCard;
  relevance_score: number;
  factors: RelevanceFactor[];
  reasons: string[];
  role: Role;
  urgent?: boolean;
  impact?: Impact;
  via_group?: boolean;
  group_id?: string | null;
  external?: boolean;
}

export interface FeedResponse {
  company: CompanySummary;
  role: Role;
  items: FeedItem[];
  scoring_config_version: string;
}

export interface NormalizedEvent {
  event_id: string;
  title: string;
  summary?: string;
  raw_text?: string;
  event_type: EventType;
  sectors?: string[];
  regions?: string[];
  countries?: string[];
  macro_factors?: MacroFactor[];
  entities?: string[];
  figures?: Figure[];
  sentiment?: Sentiment;
  risk_opportunity?: RiskOpportunity;
  is_speculation?: boolean;
  noise_score?: number;
  confidence?: number;
  source: SourceRef;
  ingested_at?: string;
}

export interface EventDetailResponse {
  event: NormalizedEvent;
}

export interface IngestRequest {
  text?: string | null;
  url?: string | null;
  title?: string | null;
}

export interface IngestResponse {
  event: NormalizedEvent;
  duplicate_of?: string | null;
}

export interface Claim {
  text: string;
  type: ClaimType;
  source_ids: string[];
  company_features?: string[];
  confidence: number;
  impact?: Impact;
}

export type TraceStepKind =
  | "PLAN"
  | "TOOL_CALL"
  | "TOOL_RESULT"
  | "CRITIC_CHECK"
  | "RETRY"
  | "COMPLETED"
  | "ERROR";

export type TraceStepStatus = "OK" | "FAILED" | "SKIPPED";

export interface TraceEvent {
  trace_id: string;
  seq: number;
  kind: TraceStepKind;
  name: string;
  status?: TraceStepStatus;
  timestamp?: string;
  source_ids?: string[];
  company_features?: string[];
  model?: string | null;
  prompt_tokens?: number | null;
  completion_tokens?: number | null;
  latency_ms?: number | null;
  payload?: Record<string, unknown>;
}

export interface InsightRequest {
  company_id: string;
  event_id: string;
  role?: Role;
}

export interface InsightResponse {
  insight_id: string;
  company_id: string;
  event_id: string;
  role: Role;
  created_at?: string;
  what_happened: Claim[];
  why_it_matters: Claim[];
  consequences: Claim[];
  actions: Claim[];
  bank_view: Claim[];
  basis: Claim[];
  relevance_score: number;
  scoring_factors: RelevanceFactor[];
  disclaimer?: string;
  trace?: Record<string, unknown>[];
}

export interface TraceResponse {
  trace_id: string;
  events: Record<string, unknown>[];
}

export interface InsightSummary {
  insight_id: string;
  company_id: string;
  event_id: string;
  event_title?: string | null;
  role: Role;
  created_at: string;
  relevance_score: number;
  top_reason?: string | null;
}

export interface InsightListResponse {
  items: InsightSummary[];
  total: number;
}

export interface Metrics {
  generated_at: string;
  events_total: number;
  insights_total: number;
  feedback_total: number;
  thumbs_up_ratio: number | null;
  source_coverage: number;
  avg_cost_rub: number | null;
  avg_latency_ms: number | null;
  llm_spent_today_rub: number;
  llm_budget_rub: number;
}

export interface FeedbackRequest {
  insight_id: string;
  company_id: string;
  user_id: string;
  role: Role;
  rating: "useful" | "not_useful" | "wrong";
  comment?: string | null;
}

export interface FeedbackResponse {
  stored: boolean;
  feedback_id: string;
}

export interface Budget {
  day: string;
  spent_rub: number;
  budget_rub: number;
  remaining_rub: number;
  model: string;
  cache_hits: number;
}

export interface SourceInfo {
  source_id: string;
  kind: "news" | "bank" | "unknown";
  name: string;
  url?: string | null;
  page?: number | null;
  published_at?: string | null;
  snippet?: string | null;
}

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  text: string;
  claim?: Claim | null;
}

export interface ErrorBody {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiErrorShape {
  error: ErrorBody;
}

export const ROLE_LABELS: Record<Role, string> = {
  CEO: "Генеральный директор",
  CFO: "Финансовый директор",
  TREASURER: "Казначей",
  CHIEF_ACCOUNTANT: "Главный бухгалтер",
  OTHER: "Другая роль",
};

export const ROLE_SHORT: Record<Role, string> = {
  CEO: "CEO",
  CFO: "CFO",
  TREASURER: "Казначей",
  CHIEF_ACCOUNTANT: "Гл. бухгалтер",
  OTHER: "Другое",
};

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  MONETARY_POLICY: "Денежно-кредитная политика",
  FX: "Валютный рынок",
  REGULATION: "Регулирование",
  SANCTIONS: "Санкции",
  LOGISTICS: "Логистика",
  COMMODITIES: "Сырьевые товары",
  DEMAND: "Спрос",
  COMPETITION: "Конкуренция",
  TAX: "Налоги",
  LABOR: "Рынок труда",
  TECHNOLOGY: "Технологии",
  OTHER: "Другое",
};

export const MACRO_FACTOR_LABELS: Record<MacroFactor, string> = {
  KEY_RATE: "Ключевая ставка",
  INFLATION: "Инфляция",
  FX_RATE: "Курс рубля",
  BOND_YIELD: "Доходность облигаций",
  COMMODITY_PRICE: "Цены на сырьё",
  DEMAND: "Спрос",
  SUPPLY_CHAIN: "Цепочки поставок",
  REGULATION: "Регулирование",
  TAX: "Налоги",
  SANCTIONS: "Санкции",
  LABOR_COST: "Стоимость труда",
  CREDIT_ACCESS: "Доступ к кредиту",
};

export const CLAIM_TYPE_LABELS: Record<ClaimType, string> = {
  FACT: "Факт",
  BANK_VIEW: "Позиция банка",
  AI_INFERENCE: "Вывод ИИ",
  HYPOTHESIS: "Гипотеза",
};

export const CLAIM_TYPE_TOOLTIPS: Record<ClaimType, string> = {
  FACT: "Подтверждено источником",
  BANK_VIEW: "Основано на аналитике Альфа-Банка",
  AI_INFERENCE: "Сформировано моделью по доступным данным",
  HYPOTHESIS: "Гипотеза модели о связи или последствии; требует проверки",
};

export const IMPACT_LABELS: Record<Impact, string> = {
  LOW: "Низкое",
  MEDIUM: "Среднее",
  HIGH: "Высокое",
};

export const IMPACT_DESCRIPTIONS: Record<Impact, string> = {
  LOW: "Низкое: фоновый контекст, действий не требуется",
  MEDIUM: "Среднее: косвенное влияние через контрагентов, сектор или группу",
  HIGH: "Высокое: прямое влияние на выручку, затраты или ликвидность в течение 30 дней",
};

export const FACTOR_NAME_LABELS: Record<string, string> = {
  sector_match: "Отрасль",
  supply_chain_exposure: "Цепочка поставок",
  product_match: "Продукты банка",
  geo_match: "География",
  scale_weight: "Масштаб",
  recency: "Свежесть",
};

export const PRODUCT_FLAG_LABELS: Record<string, string> = {
  CL_PRODUCT_RKO_MARK: "Расчётный счёт",
  CL_PRODUCT_LOA_MARK: "Кредитные продукты",
  CL_PRODUCT_DEP_MARK: "Депозиты",
  CL_PRODUCT_GAR_MARK: "Банковские гарантии",
  CL_PRODUCT_LS_MARK: "Лизинг",
  CL_PRODUCT_PAYROLL_MARK: "Зарплатный проект",
  CL_PRODUCT_FACT_MARK: "Факторинг",
};
