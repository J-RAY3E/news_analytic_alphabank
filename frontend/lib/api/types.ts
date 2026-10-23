export type Role = "CEO" | "CFO" | "TREASURER" | "CHIEF_ACCOUNTANT" | "OTHER";

export type ClaimType = "FACT" | "BANK_VIEW" | "AI_INFERENCE";

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
  trace?: Record<string, unknown>[];
}

export interface TraceResponse {
  trace_id: string;
  events: Record<string, unknown>[];
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
};

export const CLAIM_TYPE_TOOLTIPS: Record<ClaimType, string> = {
  FACT: "Подтверждено источником",
  BANK_VIEW: "Основано на аналитике Альфа-Банка",
  AI_INFERENCE: "Сформировано моделью по доступным данным",
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
