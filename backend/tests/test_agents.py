from pathlib import Path

import pytest

from app.agents.a2_news import A2NewsIntake
from app.agents.a4_retriever import A4Retriever
from app.agents.a6_interpreter import A6Interpreter
from app.agents.orchestrator import InsightOrchestrator
from app.agents.context import CaseContext
from app.agents.guard import Guard, ToolNotAllowed, company_feature_names
from app.agents.tools import build_retrieval_query
from app.config import Settings
from app.contracts import Role
from app.data.industries import load_industry_catalog
from app.data.store import DataStore
from app.llm.client import LLMError
from app.llm.config import load_llm_config
from app.news.extract import extract_event
from app.research.index import load_research_index
from app.scoring.config import load_scoring_config
from app.scoring.engine import score_event

ROOT = Path(__file__).resolve().parents[2]


class FakeLLM:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error
        self.enabled = True
        self.config = load_llm_config(ROOT / "config" / "llm.yaml")
        self.calls = []
        self.last_usage = {
            "model": self.config.routing["reasoning"],
            "prompt_tokens": 120,
            "completion_tokens": 240,
            "cost_rub": 0.01,
            "cached": False,
        }

    def complete_json(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise LLMError(self.error)
        return self.payload


def make_settings(tmp_path: Path) -> Settings:
    return Settings(
        data_dir=tmp_path,
        scoring_config=ROOT / "config" / "scoring.yaml",
        industries_config=ROOT / "config" / "industries.yaml",
        llm_config=ROOT / "config" / "llm.yaml",
        llm_enabled=True,
        llm_api_key="test-key",
    )


def make_context(settings: Settings) -> tuple[CaseContext, object]:
    store = DataStore(
        settings,
        companies_path=ROOT / "data" / "processed" / "companies.parquet",
        graph_path=ROOT / "data" / "processed" / "graph_features.parquet",
        news_path=ROOT / "data" / "news" / "events.jsonl",
    )
    company = store.company("U_57706")
    event = store.event("news:syn-001")
    graph = store.graph.loc["U_57706"].to_dict()
    index = load_research_index(str(ROOT / "data" / "index" / "research_chunks.jsonl"))
    chunks = [
        result.to_dict() for result in index.search(build_retrieval_query(event), k=3)
    ]
    context = CaseContext(
        trace_id="trace:test",
        company_id="U_57706",
        event_id="news:syn-001",
        role=Role.CFO,
        company=company,
        event=event,
    )
    context.results["get_graph_exposure"] = graph
    context.results["search_bank_analytics"] = chunks
    relevance = score_event(
        company,
        event,
        load_scoring_config(str(settings.scoring_config)),
        load_industry_catalog(str(settings.industries_config)),
        graph_row=graph,
    )
    return context, relevance


def claim(text, claim_type, sources):
    return {
        "text": text,
        "type": claim_type,
        "source_ids": sources,
        "company_features": [],
        "confidence": 0.8,
    }


def valid_ledger(bank_id: str) -> dict:
    return {
        "what_happened": [claim("Ставка сохранена на 16%.", "FACT", ["news:syn-001"])],
        "why_it_matters": [
            claim("Компания зависит от стоимости фондирования.", "AI_INFERENCE", ["news:syn-001"])
        ],
        "consequences": [
            claim("Процентные расходы останутся повышенными.", "AI_INFERENCE", [bank_id])
        ],
        "actions": [
            claim("Пересмотреть график рефинансирования.", "AI_INFERENCE", ["news:syn-001"])
        ],
        "bank_view": [claim("Ставка останется высокой дольше.", "BANK_VIEW", [bank_id])],
        "basis": [claim("Новость и research банка.", "FACT", ["news:syn-001", bank_id])],
    }


def test_a2_merges_llm_extraction(tmp_path: Path):
    settings = make_settings(tmp_path)
    catalog = load_industry_catalog(str(settings.industries_config))
    base = extract_event(
        text="Банк России сохранил ключевую ставку на уровне 16%.",
        title="Ставка 16%",
        source_url=None,
        source_name="test",
        published_at=None,
        summary="",
        catalog=catalog,
    )
    fake = FakeLLM(
        payload={
            "title": "ЦБ сохранил ставку 16%",
            "summary": "Регулятор не изменил ключевую ставку.",
            "event_type": "MONETARY_POLICY",
            "sectors": ["ALL"],
            "regions": ["Москва"],
            "countries": ["Россия"],
            "macro_factors": ["KEY_RATE"],
            "entities": ["Банк России"],
            "figures": [{"label": "ставка", "value": 16, "unit": "%"}],
            "sentiment": "NEUTRAL",
            "risk_opportunity": "BOTH",
            "is_speculation": False,
            "noise_score": 0.1,
            "confidence": 0.9,
        }
    )
    result = A2NewsIntake(settings, fake).extract(base, base.raw_text)
    assert result.method == "llm"
    assert result.event.event_id == base.event_id
    assert result.event.title == "ЦБ сохранил ставку 16%"
    assert result.event.figures[0].value == 16
    assert fake.calls


def test_a2_falls_back_when_llm_fails(tmp_path: Path):
    settings = make_settings(tmp_path)
    catalog = load_industry_catalog(str(settings.industries_config))
    base = extract_event(
        text="Минтранс повысил тарифы на перевозки.",
        title="Тарифы",
        source_url=None,
        source_name="test",
        published_at=None,
        summary="",
        catalog=catalog,
    )
    result = A2NewsIntake(settings, FakeLLM(error="timeout")).extract(base, base.raw_text)
    assert result.method == "deterministic_fallback"
    assert result.event.event_id == base.event_id


def test_a6_accepts_valid_llm_ledger(tmp_path: Path):
    settings = make_settings(tmp_path)
    context, relevance = make_context(settings)
    bank_id = context.bank_chunks[0]["source_id"]
    fake = FakeLLM(payload=valid_ledger(bank_id))
    interpretation = A6Interpreter(settings, fake).interpret(context, relevance)
    assert interpretation.method == "llm"
    assert interpretation.model == "deepseek/deepseek-v4.1-flash"
    assert interpretation.blocks["what_happened"][0].type.value == "FACT"
    assert interpretation.blocks["bank_view"][0].source_ids == [bank_id]
    assert all(block for block in interpretation.blocks.values())


def test_a6_rejects_hallucinated_sources_and_falls_back(tmp_path: Path):
    settings = make_settings(tmp_path)
    context, relevance = make_context(settings)
    ledger = valid_ledger("bank:key_rate:p1")
    ledger["what_happened"] = [claim("Выдуманный факт.", "FACT", ["news:fake"])]
    fake = FakeLLM(payload=ledger)
    interpretation = A6Interpreter(settings, fake).interpret(context, relevance)
    assert interpretation.method == "deterministic_fallback"
    assert interpretation.error
    assert interpretation.blocks["what_happened"][0].source_ids == ["news:syn-001"]


def test_guard_blocks_unknown_tools_and_writes_audit(tmp_path: Path):
    settings = make_settings(tmp_path)
    guard = Guard(settings)
    with pytest.raises(ToolNotAllowed):
        guard.authorize("delete_company", Role.CEO, {})
    guard.audit("get_event", Role.CEO, {"event_id": "news:syn-001"}, "OK", 1, 1)
    assert (tmp_path / "audit" / "tool_calls.jsonl").exists()


def test_company_features_include_product_flags(tmp_path: Path):
    settings = make_settings(tmp_path)
    context, _ = make_context(settings)
    features = company_feature_names(context.company, context.graph)
    assert "CL_PRODUCT_RKO_MARK" in features
    assert "has_payment_activity" in features


def test_a4_retriever_returns_cited_bank_chunks(tmp_path: Path):
    settings = make_settings(tmp_path)
    context, _ = make_context(settings)
    retriever = A4Retriever(
        load_research_index(str(ROOT / "data" / "index" / "research_chunks.jsonl"))
    )
    results = retriever.search_event(context.event, k=4)
    assert results
    assert all(result["source_id"].startswith("bank:") for result in results)
    assert all(result["score"] > 0 for result in results)
    assert all(result["text"] and result["page"] >= 1 for result in results)


def test_orchestrator_llm_path_persists_insight_and_trace(tmp_path: Path):
    settings = make_settings(tmp_path)
    store = DataStore(
        settings,
        companies_path=ROOT / "data" / "processed" / "companies.parquet",
        graph_path=ROOT / "data" / "processed" / "graph_features.parquet",
        news_path=ROOT / "data" / "news" / "events.jsonl",
    )
    index = load_research_index(str(ROOT / "data" / "index" / "research_chunks.jsonl"))
    chunks = [
        result.to_dict()
        for result in index.search(
            build_retrieval_query(store.event("news:syn-001")), k=2
        )
    ]
    fake = FakeLLM(payload=valid_ledger(chunks[0]["source_id"]))
    insight = InsightOrchestrator(settings, store, index=index, llm=fake).run(
        "U_57706", "news:syn-001", Role.CFO
    )
    assert all(getattr(insight, block) for block in (
        "what_happened",
        "why_it_matters",
        "consequences",
        "actions",
        "bank_view",
        "basis",
    ))
    last = insight.trace[-1]
    assert last.kind.value == "COMPLETED"
    assert last.payload["method"] == "llm"
    assert last.model == "deepseek/deepseek-v4.1-flash"
    assert last.prompt_tokens == 120
    assert last.completion_tokens == 240
    assert {event.kind.value for event in insight.trace} >= {
        "PLAN",
        "TOOL_CALL",
        "TOOL_RESULT",
        "COMPLETED",
    }
    insight_path = tmp_path / "insights" / f"{insight.insight_id.replace(':', '_')}.json"
    trace_path = tmp_path / "traces" / f"{insight.trace[0].trace_id}.json"
    assert insight_path.exists()
    assert trace_path.exists()
    allowed = {"news:syn-001"} | {chunk["source_id"] for chunk in chunks}
    for block in (
        "what_happened",
        "why_it_matters",
        "consequences",
        "actions",
        "bank_view",
        "basis",
    ):
        for item in getattr(insight, block):
            assert set(item.source_ids) <= allowed
