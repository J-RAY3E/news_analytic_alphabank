import type {
  CompanySummary,
  FeedEventCard,
  FeedItem,
  InsightResponse,
  NormalizedEvent,
  RelevanceFactor,
  Role,
  TraceEvent,
} from "@/lib/api/types";

export const DEMO_USERS = [
  { id: "user-ceo", name: "Директор по стратегии", role: "CEO" as Role },
  { id: "user-cfo", name: "Финансовый директор", role: "CFO" as Role },
];

export const MOCK_COMPANIES: CompanySummary[] = [
  {
    company_id: "CL_001",
    display_name: "Клиент 001",
    okved_code: "24.51",
    okved_name: "Производство чугуна, стали и ферросплавов",
    okved_division: "24",
    okved_section: "C",
    industry_label: "Металлургия",
    region: "Свердловская область",
    city: "Екатеринбург",
    revenue_rub: 42_500_000_000,
    revenue_band: "35-50 млрд руб.",
    employees_band: "1000-5000",
    client_type: "Крупный бизнес",
    product_flags: ["CL_PRODUCT_RKO_MARK", "CL_PRODUCT_LOA_MARK", "CL_PRODUCT_GAR_MARK"],
    is_exporter: true,
    fts_countries: ["Китай", "Турция"],
    group_id: "GRP_10",
    group_size: 4,
  },
  {
    company_id: "CL_002",
    display_name: "Клиент 002",
    okved_code: "01.11",
    okved_name: "Выращивание зерновых культур",
    okved_division: "01",
    okved_section: "A",
    industry_label: "Сельское хозяйство",
    region: "Краснодарский край",
    city: "Краснодар",
    revenue_rub: 18_200_000_000,
    revenue_band: "15-25 млрд руб.",
    employees_band: "500-1000",
    client_type: "Крупный бизнес",
    product_flags: ["CL_PRODUCT_RKO_MARK", "CL_PRODUCT_DEP_MARK", "CL_PRODUCT_PAYROLL_MARK"],
    is_exporter: true,
    fts_countries: ["Турция"],
    group_id: null,
    group_size: 1,
  },
  {
    company_id: "CL_003",
    display_name: "Клиент 003",
    okved_code: "49.41",
    okved_name: "Деятельность автомобильного грузового транспорта",
    okved_division: "49",
    okved_section: "H",
    industry_label: "Логистика",
    region: "Москва",
    city: "Москва",
    revenue_rub: 25_400_000_000,
    revenue_band: "25-35 млрд руб.",
    employees_band: "500-1000",
    client_type: "Крупный бизнес",
    product_flags: ["CL_PRODUCT_RKO_MARK", "CL_PRODUCT_LOA_MARK", "CL_PRODUCT_FACT_MARK"],
    is_exporter: false,
    fts_countries: [],
    group_id: "GRP_21",
    group_size: 2,
  },
  {
    company_id: "CL_004",
    display_name: "Клиент 004",
    okved_code: "47.11",
    okved_name: "Торговля розничная в неспециализированных магазинах",
    okved_division: "47",
    okved_section: "G",
    industry_label: "Торговля",
    region: "Москва",
    city: "Москва",
    revenue_rub: 60_800_000_000,
    revenue_band: "50-75 млрд руб.",
    employees_band: "5000-10000",
    client_type: "Крупный бизнес",
    product_flags: [
      "CL_PRODUCT_RKO_MARK",
      "CL_PRODUCT_LOA_MARK",
      "CL_PRODUCT_DEP_MARK",
      "CL_PRODUCT_PAYROLL_MARK",
    ],
    is_exporter: false,
    fts_countries: [],
    group_id: "GRP_30",
    group_size: 7,
  },
  {
    company_id: "CL_005",
    display_name: "Клиент 005",
    okved_code: "20.14",
    okved_name: "Производство прочих основных органических химических веществ",
    okved_division: "20",
    okved_section: "C",
    industry_label: "Химическая промышленность",
    region: "Самарская область",
    city: "Тольятти",
    revenue_rub: 88_300_000_000,
    revenue_band: "75-100 млрд руб.",
    employees_band: "5000-10000",
    client_type: "Крупный бизнес",
    product_flags: [
      "CL_PRODUCT_RKO_MARK",
      "CL_PRODUCT_LOA_MARK",
      "CL_PRODUCT_DEP_MARK",
      "CL_PRODUCT_GAR_MARK",
      "CL_PRODUCT_LS_MARK",
    ],
    is_exporter: true,
    fts_countries: ["Китай", "Индия"],
    group_id: "GRP_44",
    group_size: 5,
  },
];

function factor(
  name: string,
  value: number,
  weight: number,
  explanation: string
): RelevanceFactor {
  return { name, value, weight, contribution: Number((value * weight).toFixed(4)), explanation };
}

interface EventSeed {
  event: NormalizedEvent;
  factorValues: (c: CompanySummary) => Record<string, { v: number; expl: string }>;
  reasons: (c: CompanySummary) => string[];
}

const PUBLISHED_JULY = (day: number, hour: number) => `2026-07-${String(day).padStart(2, "0")}T${String(hour).padStart(2, "0")}:10:00+03:00`;

const EVENT_SEEDS: EventSeed[] = [
  {
    event: {
      event_id: "news:rate-note-0725",
      title: "ЦБ сохранил ключевую ставку на уровне 14,0% годовых",
      summary:
        "Совет директоров Банка России оставил ключевую ставку без изменений на уровне 14,0% годовых. Регулятор отметил замедление инфляции, но сохраняет жёсткую денежно-кредитную политику.",
      event_type: "MONETARY_POLICY",
      sectors: ["Металлургия", "Строительство", "Торговля"],
      regions: ["Россия"],
      countries: ["Россия"],
      macro_factors: ["KEY_RATE", "CREDIT_ACCESS"],
      entities: ["Банк России"],
      figures: [{ label: "Ключевая ставка", value: 14.0, unit: "%" }],
      sentiment: "NEUTRAL",
      risk_opportunity: "NEUTRAL",
      source: {
        source_id: "news:rate-note-0725",
        name: "Интерфакс",
        url: "https://example.com/news/rate-note-0725",
        published_at: PUBLISHED_JULY(25, 13),
        language: "ru",
      },
      ingested_at: PUBLISHED_JULY(25, 13),
    },
    factorValues: (c) => ({
      sector_match: {
        v: c.industry_label === "Металлургия" ? 0.8 : 0.4,
        expl: "Отрасль компании чувствительна к стоимости заёмного финансирования",
      },
      supply_chain_exposure: { v: 0.3, expl: "Ставка слабо влияет на цепочки поставок" },
      product_match: {
        v: c.product_flags.includes("CL_PRODUCT_LOA_MARK") ? 0.9 : 0.1,
        expl: "У компании есть кредитные продукты, привязанные к ключевой ставке",
      },
      geo_match: { v: 0.7, expl: "Событие действует на всей территории РФ" },
      scale_weight: { v: 0.6, expl: "Крупный клиент с существенным долговым портфелем" },
      recency: { v: 1.0, expl: "Новость опубликована сегодня" },
    }),
    reasons: (c) => [
      c.product_flags.includes("CL_PRODUCT_LOA_MARK")
        ? "У вас есть кредитные продукты, а ключевая ставка сохранилась на уровне 14,0%"
        : "Ставка влияет на стоимость финансирования в вашей отрасли",
    ],
  },
  {
    event: {
      event_id: "news:fx-strength-0724",
      title: "Рубль укрепился до 78,2 за доллар на фоне экспортных продаж",
      summary:
        "Курс доллара опустился до 78,2 рубля. Аналитики связывают укрепление с ростом поступлений экспортёров и снижением спроса на импорт.",
      event_type: "FX",
      sectors: ["Металлургия", "Химическая промышленность", "Сельское хозяйство"],
      regions: ["Россия"],
      countries: ["Россия"],
      macro_factors: ["FX_RATE"],
      entities: ["Мосбиржа"],
      figures: [{ label: "Курс USD/RUB", value: 78.2, unit: "руб." }],
      sentiment: "MIXED",
      risk_opportunity: "BOTH",
      source: {
        source_id: "news:fx-strength-0724",
        name: "РБК",
        url: "https://example.com/news/fx-strength-0724",
        published_at: PUBLISHED_JULY(24, 19),
        language: "ru",
      },
      ingested_at: PUBLISHED_JULY(24, 19),
    },
    factorValues: (c) => ({
      sector_match: { v: 0.5, expl: "Отрасль частично зависит от валютной выручки" },
      supply_chain_exposure: { v: 0.2, expl: "Прямая связь с поставками не выявлена" },
      product_match: { v: 0.2, expl: "Продуктовая связь слабая" },
      geo_match: {
        v: c.is_exporter ? 0.9 : 0.5,
        expl: c.is_exporter
          ? "Компания экспортирует и получает валютную выручку"
          : "Событие общерыночное",
      },
      scale_weight: { v: 0.6, expl: "Крупный клиент" },
      recency: { v: 0.8, expl: "Новость вчерашняя" },
    }),
    reasons: (c) => [
      c.is_exporter
        ? "Вы экспортируете продукцию: укрепление рубля снижает выручку в рублях"
        : "Курс рубля влияет на закупочные цены в вашей отрасли",
    ],
  },
  {
    event: {
      event_id: "news:sanctions-metal-0723",
      title: "Расширен санкционный список для поставок металлургического оборудования",
      summary:
        "Введены ограничения на поставку оборудования для металлургических предприятий из недружественных стран. Под ограничениями линии горячей прокатки и системы автоматизации.",
      event_type: "SANCTIONS",
      sectors: ["Металлургия"],
      regions: ["Россия"],
      countries: ["ЕС", "США"],
      macro_factors: ["SANCTIONS", "SUPPLY_CHAIN"],
      entities: ["Европейская комиссия"],
      figures: [],
      sentiment: "NEGATIVE",
      risk_opportunity: "RISK",
      source: {
        source_id: "news:sanctions-metal-0723",
        name: "Ведомости",
        url: "https://example.com/news/sanctions-metal-0723",
        published_at: PUBLISHED_JULY(23, 11),
        language: "ru",
      },
      ingested_at: PUBLISHED_JULY(23, 11),
    },
    factorValues: (c) => ({
      sector_match: { v: c.industry_label === "Металлургия" ? 1.0 : 0.2, expl: "Ограничения касаются отрасли компании" },
      supply_chain_exposure: {
        v: c.industry_label === "Металлургия" ? 0.8 : 0.3,
        expl: "У компании есть поставщики в затронутых категориях оборудования",
      },
      product_match: { v: 0.3, expl: "Банковские гарантии применяются в импортных контрактах" },
      geo_match: {
        v: c.fts_countries.length > 0 ? 0.7 : 0.4,
        expl: "Компания имеет внешнеэкономические операции",
      },
      scale_weight: { v: 0.6, expl: "Крупный клиент" },
      recency: { v: 0.6, expl: "Новость двухдневной давности" },
    }),
    reasons: (c) => [
      c.industry_label === "Металлургия"
        ? "Ограничения касаются вашей отрасли и поставщиков оборудования"
        : "Событие затрагивает смежные отрасли вашей цепочки поставок",
    ],
  },
  {
    event: {
      event_id: "news:logistics-baltic-0722",
      title: "Очереди в портах Балтики выросли на 30% из-за погодных ограничений",
      summary:
        "Штормовые предупреждения замедлили обработку судов в портах Санкт-Петербурга и Усть-Луги. Среднее время ожидания выросло до 6 дней.",
      event_type: "LOGISTICS",
      sectors: ["Логистика", "Металлургия", "Сельское хозяйство"],
      regions: ["Северо-Западный ФО"],
      countries: ["Россия"],
      macro_factors: ["SUPPLY_CHAIN"],
      entities: ["Порт Санкт-Петербурга"],
      figures: [{ label: "Среднее ожидание", value: 6, unit: "дней" }],
      sentiment: "NEGATIVE",
      risk_opportunity: "RISK",
      source: {
        source_id: "news:logistics-baltic-0722",
        name: "Коммерсантъ",
        url: "https://example.com/news/logistics-baltic-0722",
        published_at: PUBLISHED_JULY(22, 9),
        language: "ru",
      },
      ingested_at: PUBLISHED_JULY(22, 9),
    },
    factorValues: (c) => ({
      sector_match: { v: 0.4, expl: "Отрасль зависит от морских перевозок частично" },
      supply_chain_exposure: {
        v: c.fts_countries.length > 0 ? 0.7 : 0.5,
        expl: "Часть поставок идёт через балтийские порты",
      },
      product_match: { v: 0.2, expl: "Продуктовая связь слабая" },
      geo_match: { v: 0.5, expl: "Затронут северо-западный маршрут" },
      scale_weight: { v: 0.6, expl: "Крупный клиент" },
      recency: { v: 0.4, expl: "Новость трёхдневной давности" },
    }),
    reasons: () => ["Часть ваших поставок проходит через балтийские порты"],
  },
  {
    event: {
      event_id: "news:steel-prices-0721",
      title: "Цены на стальной прокат в Азии снизились на 4% за неделю",
      summary:
        "Биржевые котировки на горячекатаный прокат в Китае опустились до минимумов за квартал. Причина: снижение строительной активности и рост предложения.",
      event_type: "COMMODITIES",
      sectors: ["Металлургия"],
      regions: ["Азия"],
      countries: ["Китай"],
      macro_factors: ["COMMODITY_PRICE", "DEMAND"],
      entities: ["Шанхайская фьючерсная биржа"],
      figures: [{ label: "Изменение цены", value: -4, unit: "%" }],
      sentiment: "NEGATIVE",
      risk_opportunity: "RISK",
      source: {
        source_id: "news:steel-prices-0721",
        name: "Reuters",
        url: "https://example.com/news/steel-prices-0721",
        published_at: PUBLISHED_JULY(21, 8),
        language: "en",
      },
      ingested_at: PUBLISHED_JULY(21, 8),
    },
    factorValues: (c) => ({
      sector_match: { v: c.industry_label === "Металлургия" ? 1.0 : 0.1, expl: "Ключевая товарная позиция вашей отрасли" },
      supply_chain_exposure: { v: 0.4, expl: "Влияет на ценообразование поставщиков" },
      product_match: { v: 0.2, expl: "Продуктовая связь слабая" },
      geo_match: { v: c.fts_countries.includes("Китай") ? 0.9 : 0.3, expl: "Экспортные поставки в Китай" },
      scale_weight: { v: 0.6, expl: "Крупный клиент" },
      recency: { v: 0.2, expl: "Новость четырёхдневной давности" },
    }),
    reasons: (c) => [
      c.fts_countries.includes("Китай")
        ? "Вы поставляете продукцию в Китай, где упали цены на прокат"
        : "Мировые цены на сталь влияют на вашу отрасль",
    ],
  },
  {
    event: {
      event_id: "news:tax-rd-0720",
      title: "Минтфин предложил расширить вычеты по налогу на прибыль для НИОКР",
      summary:
        "Министерство финансов внесло законопроект о расширении перечня расходов на НИОКР, уменьшающих налоговую базу. Изменения планируются с 2027 года.",
      event_type: "TAX",
      sectors: ["Все отрасли"],
      regions: ["Россия"],
      countries: ["Россия"],
      macro_factors: ["TAX", "REGULATION"],
      entities: ["Минфин России"],
      figures: [],
      sentiment: "POSITIVE",
      risk_opportunity: "OPPORTUNITY",
      source: {
        source_id: "news:tax-rd-0720",
        name: "РИА Новости",
        url: "https://example.com/news/tax-rd-0720",
        published_at: PUBLISHED_JULY(20, 14),
        language: "ru",
      },
      ingested_at: PUBLISHED_JULY(20, 14),
    },
    factorValues: () => ({
      sector_match: { v: 0.5, expl: "Мера действует на все отрасли" },
      supply_chain_exposure: { v: 0.1, expl: "Связи с поставками нет" },
      product_match: { v: 0.3, expl: "Актуально при наличии кредитных продуктов" },
      geo_match: { v: 0.7, expl: "Российская юрисдикция" },
      scale_weight: { v: 0.6, expl: "Крупный клиент" },
      recency: { v: 0.2, expl: "Новость пятидневной давности" },
    }),
    reasons: () => ["Налоговая инициатива может снизить вашу налоговую нагрузку"],
  },
];

export function buildMockFeed(company: CompanySummary, role: Role): FeedItem[] {
  return EVENT_SEEDS.map((seed) => {
    const fv = seed.factorValues(company);
    const factors = Object.entries(fv).map(([name, { v, expl }]) =>
      factor(
        name,
        v,
        {
          sector_match: 0.3,
          supply_chain_exposure: 0.2,
          product_match: 0.2,
          geo_match: 0.15,
          scale_weight: 0.1,
          recency: 0.05,
        }[name] ?? 0,
        expl
      )
    );
    const score = factors.reduce((acc, f) => acc + f.contribution, 0);
    const reasons = seed.reasons(company);
    if (role === "CFO" && seed.event.event_type === "MONETARY_POLICY") {
      reasons.push("Для роли CFO: стоимость обслуживания долга и ковенанты");
    }
    if (role === "TREASURER" && seed.event.event_type === "MONETARY_POLICY") {
      reasons.push("Для роли казначея: доходность депозитов и ликвидность");
    }
    const src = seed.event.source;
    const card: FeedEventCard = {
      event_id: seed.event.event_id,
      title: seed.event.title,
      summary: seed.event.summary ?? "",
      event_type: seed.event.event_type,
      sectors: seed.event.sectors ?? [],
      regions: seed.event.regions ?? [],
      countries: seed.event.countries ?? [],
      macro_factors: seed.event.macro_factors ?? [],
      sentiment: seed.event.sentiment ?? "NEUTRAL",
      risk_opportunity: seed.event.risk_opportunity ?? "NEUTRAL",
      published_at: src.published_at ?? null,
      source_name: src.name,
      source_url: src.url ?? null,
    };
    return {
      event: card,
      relevance_score: Number(score.toFixed(4)),
      factors,
      reasons,
      role,
    };
  }).sort((a, b) => b.relevance_score - a.relevance_score);
}

export function getMockEvent(eventId: string): NormalizedEvent | null {
  const seed = EVENT_SEEDS.find((s) => s.event.event_id === eventId);
  return seed ? seed.event : null;
}

export const MOCK_TRACE: TraceEvent[] = [
  {
    trace_id: "trace-demo-001",
    seq: 0,
    kind: "PLAN",
    name: "plan_write",
    status: "OK",
    timestamp: "2026-07-25T13:12:01+03:00",
    model: "GLM-5.3-Flash",
    prompt_tokens: 820,
    completion_tokens: 210,
    latency_ms: 1400,
    payload: {
      steps: [
        "Профиль компании и продукты",
        "Экспозиция поставщиков",
        "Поиск позиции банка",
        "Интерпретация для роли",
        "Проверка Critic",
      ],
    },
  },
  {
    trace_id: "trace-demo-001",
    seq: 1,
    kind: "TOOL_CALL",
    name: "get_company_profile",
    status: "OK",
    timestamp: "2026-07-25T13:12:02+03:00",
    latency_ms: 120,
    company_features: ["CL_PRODUCT_LOA_MARK", "okved2", "revenue_band"],
  },
  {
    trace_id: "trace-demo-001",
    seq: 2,
    kind: "TOOL_RESULT",
    name: "get_company_profile",
    status: "OK",
    timestamp: "2026-07-25T13:12:02+03:00",
    latency_ms: 45,
    payload: {
      industry: "Металлургия",
      products: ["Кредитные продукты", "Гарантии", "Расчётный счёт"],
      revenue_band: "35-50 млрд руб.",
    },
  },
  {
    trace_id: "trace-demo-001",
    seq: 3,
    kind: "TOOL_CALL",
    name: "get_graph_exposure",
    status: "OK",
    timestamp: "2026-07-25T13:12:03+03:00",
    latency_ms: 180,
    company_features: ["top_suppliers_okved", "supplier_concentration"],
  },
  {
    trace_id: "trace-demo-001",
    seq: 4,
    kind: "TOOL_RESULT",
    name: "get_graph_exposure",
    status: "OK",
    timestamp: "2026-07-25T13:12:03+03:00",
    latency_ms: 60,
    payload: {
      top_supplier_industries: ["Металлургия", "Машиностроение"],
      supplier_concentration: 0.34,
    },
  },
  {
    trace_id: "trace-demo-001",
    seq: 5,
    kind: "TOOL_CALL",
    name: "search_bank_analytics",
    status: "OK",
    timestamp: "2026-07-25T13:12:04+03:00",
    latency_ms: 640,
    model: null,
    source_ids: ["bank:rate_note:p2", "bank:macro_stat:p5"],
  },
  {
    trace_id: "trace-demo-001",
    seq: 6,
    kind: "TOOL_RESULT",
    name: "search_bank_analytics",
    status: "OK",
    timestamp: "2026-07-25T13:12:04+03:00",
    latency_ms: 210,
    source_ids: ["bank:rate_note:p2", "bank:macro_stat:p5"],
    payload: {
      stance: "Банк ожидает удержания ставки до конца III квартала при замедлении инфляции",
    },
  },
  {
    trace_id: "trace-demo-001",
    seq: 7,
    kind: "TOOL_CALL",
    name: "interpret_insight",
    status: "OK",
    timestamp: "2026-07-25T13:12:06+03:00",
    model: "GLM-5.3-Flash",
    prompt_tokens: 2400,
    completion_tokens: 980,
    latency_ms: 3200,
    company_features: ["CL_PRODUCT_LOA_MARK", "supplier_concentration"],
  },
  {
    trace_id: "trace-demo-001",
    seq: 8,
    kind: "CRITIC_CHECK",
    name: "source_coverage",
    status: "OK",
    timestamp: "2026-07-25T13:12:07+03:00",
    latency_ms: 90,
    payload: { coverage: 1.0, claims_checked: 11 },
  },
  {
    trace_id: "trace-demo-001",
    seq: 9,
    kind: "CRITIC_CHECK",
    name: "numeric_consistency",
    status: "FAILED",
    timestamp: "2026-07-25T13:12:07+03:00",
    latency_ms: 110,
    payload: {
      issue: "Заявление содержит ставку 16,0%, в источнике указано 14,0%",
      claim_index: 2,
    },
  },
  {
    trace_id: "trace-demo-001",
    seq: 10,
    kind: "RETRY",
    name: "Пересмотр числовых данных",
    status: "OK",
    timestamp: "2026-07-25T13:12:08+03:00",
    model: "GLM-5.3-Flash",
    prompt_tokens: 950,
    completion_tokens: 240,
    latency_ms: 1500,
    payload: { action: "Исправление ставки в блоке последствий" },
  },
  {
    trace_id: "trace-demo-001",
    seq: 11,
    kind: "CRITIC_CHECK",
    name: "numeric_consistency",
    status: "OK",
    timestamp: "2026-07-25T13:12:09+03:00",
    latency_ms: 80,
    payload: { claims_checked: 11 },
  },
  {
    trace_id: "trace-demo-001",
    seq: 12,
    kind: "COMPLETED",
    name: "insight_ready",
    status: "OK",
    timestamp: "2026-07-25T13:12:10+03:00",
    latency_ms: 9200,
  },
];

export function buildMockInsight(
  company: CompanySummary,
  eventId: string,
  role: Role
): InsightResponse {
  const feed = buildMockFeed(company, role);
  const item = feed.find((i) => i.event.event_id === eventId) ?? feed[0];

  const roleWhy: Record<Role, string> = {
    CEO: "Событие меняет условия финансирования и конкурентную позицию компании, что влияет на стратегические планы развития и ценовую политику.",
    CFO: "Сохранение ставки 14,0% фиксирует высокую стоимость долга: обслуживание кредитного портфеля и условия ковенант остаются без изменений до следующего заседания.",
    TREASURER: "Ставка влияет на доходность депозитов и стоимость привлечения ликвидности: размещения под высокие проценты остаются привлекательными.",
    CHIEF_ACCOUNTANT: "Изменений в налоговой и отчётной практике нет, но стоимость кредита отражается в учётных оценках дисконтирования.",
    OTHER: "Событие определяет общий фон стоимости денег для компании и её контрагентов.",
  };

  const roleActions: Record<Role, string[]> = {
    CEO: [
      "Проверить план капитальных вложений на чувствительность к ставке 14,0% (CL_PRODUCT_LOA_MARK)",
      "Оценить альтернативные источники финансирования перед следующим заседанием ЦБ",
    ],
    CFO: [
      "Зафиксировать текущие ставки по действующим кредитным линиям (CL_PRODUCT_LOA_MARK)",
      "Проверить исполнение ковенант при текущей стоимости долга",
    ],
    TREASURER: [
      "Рассмотреть размещение свободной ликвидности на депозит до следующего заседания ЦБ",
      "Составить график платежей по кредитам с учётом сохранения ставки",
    ],
    CHIEF_ACCOUNTANT: [
      "Проверить ставки дисконтирования, применяемые в отчётности",
    ],
    OTHER: [
      "Отслеживать решения ЦБ в области денежно-кредитной политики",
    ],
  };

  return {
    insight_id: `ins_${company.company_id}_${eventId.replace("news:", "")}_${role}`,
    company_id: company.company_id,
    event_id: eventId,
    role,
    created_at: "2026-07-25T13:12:10+03:00",
    what_happened: [
      {
        text: "Совет директоров Банка России сохранил ключевую ставку на уровне 14,0% годовых.",
        type: "FACT",
        source_ids: ["news:rate-note-0725"],
        company_features: [],
        confidence: 0.98,
      },
      {
        text: "Регулятор указал на замедление инфляции, но сохранил жёсткую денежно-кредитную политику.",
        type: "FACT",
        source_ids: ["news:rate-note-0725"],
        company_features: [],
        confidence: 0.95,
      },
    ],
    why_it_matters: [
      {
        text: roleWhy[role],
        type: "AI_INFERENCE",
        source_ids: ["news:rate-note-0725"],
        company_features: ["CL_PRODUCT_LOA_MARK", "revenue_band"],
        confidence: 0.82,
      },
      {
        text: "Компания имеет кредитные продукты, привязанные к ключевой ставке, поэтому стоимость обслуживания долга не изменится.",
        type: "AI_INFERENCE",
        source_ids: ["news:rate-note-0725"],
        company_features: ["CL_PRODUCT_LOA_MARK"],
        confidence: 0.88,
      },
    ],
    consequences: [
      {
        text: "Стоимость нового заёмного финансирования останется высокой как минимум до следующего заседания ЦБ.",
        type: "AI_INFERENCE",
        source_ids: ["news:rate-note-0725", "bank:rate_note:p2"],
        company_features: ["CL_PRODUCT_LOA_MARK"],
        confidence: 0.78,
      },
      {
        text: "Доходность депозитных продуктов сохранится на привлекательном уровне для размещения ликвидности.",
        type: "AI_INFERENCE",
        source_ids: ["bank:rate_note:p2"],
        company_features: ["CL_PRODUCT_DEP_MARK"],
        confidence: 0.74,
      },
    ],
    actions: roleActions[role].map((text) => ({
      text,
      type: "AI_INFERENCE" as const,
      source_ids: ["news:rate-note-0725"],
      company_features: ["CL_PRODUCT_LOA_MARK"],
      confidence: 0.8,
    })),
    bank_view: [
      {
        text: "Альфа-Банк ожидает удержания ключевой ставки до конца III квартала 2026 года при сохранении тенденции замедления инфляции.",
        type: "BANK_VIEW",
        source_ids: ["bank:rate_note:p2"],
        company_features: [],
        confidence: 0.92,
      },
      {
        text: "По оценке аналитиков банка, инфляция замедлится к концу года, что создаёт предпосылки для смягчения политики в IV квартале.",
        type: "BANK_VIEW",
        source_ids: ["bank:macro_stat:p5"],
        company_features: [],
        confidence: 0.9,
      },
    ],
    basis: [
      {
        text: "Новость «ЦБ сохранил ключевую ставку на уровне 14,0% годовых» (Интерфакс, 25 июля).",
        type: "FACT",
        source_ids: ["news:rate-note-0725"],
        company_features: [],
        confidence: 0.98,
      },
      {
        text: "Аналитика Альфа-Банка: обзор ключевой ставки, страница 2; макростатистика 7М26, страница 5.",
        type: "BANK_VIEW",
        source_ids: ["bank:rate_note:p2", "bank:macro_stat:p5"],
        company_features: [],
        confidence: 0.92,
      },
      {
        text: "Учтённые признаки компании: кредитные продукты, выручка 35-50 млрд руб., концентрация поставщиков 34%.",
        type: "AI_INFERENCE",
        source_ids: [],
        company_features: ["CL_PRODUCT_LOA_MARK", "revenue_band", "supplier_concentration"],
        confidence: 0.85,
      },
    ],
    relevance_score: item.relevance_score,
    scoring_factors: item.factors,
    trace: MOCK_TRACE as unknown as Record<string, unknown>[],
  };
}

export const MOCK_SOURCES: Record<string, { name: string; url: string | null; page: number | null }> = {
  "news:rate-note-0725": {
    name: "Интерфакс: ЦБ сохранил ключевую ставку",
    url: "https://example.com/news/rate-note-0725",
    page: null,
  },
  "news:fx-strength-0724": {
    name: "РБК: Рубль укрепился до 78,2 за доллар",
    url: "https://example.com/news/fx-strength-0724",
    page: null,
  },
  "news:sanctions-metal-0723": {
    name: "Ведомости: Расширен санкционный список",
    url: "https://example.com/news/sanctions-metal-0723",
    page: null,
  },
  "news:logistics-baltic-0722": {
    name: "Коммерсантъ: Очереди в портах Балтики",
    url: "https://example.com/news/logistics-baltic-0722",
    page: null,
  },
  "news:steel-prices-0721": {
    name: "Reuters: Цены на стальной прокат снизились",
    url: "https://example.com/news/steel-prices-0721",
    page: null,
  },
  "news:tax-rd-0720": {
    name: "РИА Новости: Вычеты по НИОКР",
    url: "https://example.com/news/tax-rd-0720",
    page: null,
  },
  "bank:rate_note:p2": {
    name: "Альфа-Банк: Обзор ключевой ставки, страница 2",
    url: null,
    page: 2,
  },
  "bank:macro_stat:p5": {
    name: "Альфа-Банк: Макростатистика 7М26, страница 5",
    url: null,
    page: 5,
  },
};
