from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.data.store import DataStore
from app.main import app
from app.contracts import Role

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    settings = Settings(
        data_dir=tmp_path,
        scoring_config=ROOT / "config" / "scoring.yaml",
        industries_config=ROOT / "config" / "industries.yaml",
        llm_config=ROOT / "config" / "llm.yaml",
        llm_enabled=False,
    )
    news_path = tmp_path / "news" / "events.jsonl"
    news_path.parent.mkdir(parents=True, exist_ok=True)
    source_news = ROOT / "data" / "news" / "events.jsonl"
    if source_news.exists():
        news_path.write_text(source_news.read_text(encoding="utf-8"), encoding="utf-8")
    source_index = ROOT / "data" / "index" / "research_chunks.jsonl"
    if source_index.exists():
        index_path = tmp_path / "index" / "research_chunks.jsonl"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(source_index.read_text(encoding="utf-8"), encoding="utf-8")
    app.state.settings = settings
    app.state.store = DataStore(
        settings,
        companies_path=PROCESSED / "companies.parquet",
        graph_path=PROCESSED / "graph_features.parquet",
        news_path=news_path,
    )
    return TestClient(app)


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["data"]["companies"] is True


def test_companies_endpoint_and_target_filter(client: TestClient):
    response = client.get("/companies", params={"limit": 5, "target_only": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 100
    assert len(payload["items"]) == 5
    assert all(item["revenue_rub"] >= 15_000_000_000 for item in payload["items"])
    assert all(item["display_name"] for item in payload["items"])


def test_company_not_found(client: TestClient):
    response = client.get("/companies/U_DOES_NOT_EXIST")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_feed_endpoint_scores_are_ordered(client: TestClient):
    response = client.get(
        "/feed", params={"company_id": "U_57706", "role": Role.CFO.value, "limit": 5}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["company"]["company_id"] == "U_57706"
    assert payload["role"] == "CFO"
    assert len(payload["items"]) == 5
    scores = [item["relevance_score"] for item in payload["items"]]
    assert scores == sorted(scores, reverse=True)
    assert all(0.0 <= score <= 1.0 for score in scores)
    assert all(len(item["factors"]) == 6 for item in payload["items"])
    assert all(item["reasons"] for item in payload["items"])
    assert all(item["event"]["event_id"].startswith("news:") for item in payload["items"])


def test_event_detail(client: TestClient):
    response = client.get("/events/news:syn-001")
    assert response.status_code == 200
    assert response.json()["event"]["title"].startswith("Банк России")


def test_ingest_and_duplicate(client: TestClient):
    payload = {
        "text": "Минтранс предложил повысить тарифы на перевозки на 12% с января.",
        "title": "Рост тарифов на перевозки",
    }
    first = client.post("/ingest", json=payload)
    assert first.status_code == 200
    assert first.json()["duplicate_of"] is None

    second = client.post("/ingest", json=payload)
    assert second.status_code == 200
    assert second.json()["duplicate_of"] == first.json()["event"]["event_id"]


def test_ingest_requires_text_or_url(client: TestClient):
    response = client.post("/ingest", json={})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "bad_request"


def test_insight_pipeline_and_trace(client: TestClient):
    response = client.post(
        "/insight",
        json={"company_id": "U_57706", "event_id": "news:syn-001", "role": "CFO"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["insight_id"].startswith("insight:")
    assert payload["role"] == "CFO"
    assert payload["what_happened"]
    assert payload["why_it_matters"]
    assert payload["consequences"]
    assert payload["actions"]
    assert payload["bank_view"]
    assert payload["basis"]
    assert 0.0 <= payload["relevance_score"] <= 1.0
    assert len(payload["scoring_factors"]) == 6
    assert payload["trace"]
    trace_id = payload["trace"][0]["trace_id"]
    trace = client.get(f"/trace/{trace_id}")
    assert trace.status_code == 200
    assert trace.json()["trace_id"] == trace_id
    assert trace.json()["events"]


def test_feedback_persists(client: TestClient):
    payload = {
        "insight_id": "insight:test",
        "company_id": "U_57706",
        "user_id": "user:test",
        "role": "CFO",
        "rating": "useful",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["stored"] is True
    assert (ROOT / "data" / "feedback" / "feedback.jsonl").exists() or response.json()[
        "feedback_id"
    ].startswith("feedback:")


def test_validation_error_format(client: TestClient):
    response = client.get("/feed", params={"company_id": "", "role": "INVALID"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["details"]["errors"]
