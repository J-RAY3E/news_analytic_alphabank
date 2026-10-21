import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.config import Settings
from app.contracts import NormalizedEvent
from app.data.store import DataStore
from app.news.extract import (
    build_event_id,
    detect_countries,
    detect_event_type,
    detect_macro_factors,
    estimate_noise,
    extract_event,
    extract_text_from_html,
    parse_rss,
    validate_public_url,
)
from app.news.ingest import ingest_event
from app.news.normalize import (
    canonical_title,
    dedupe_events,
    event_similarity,
    find_duplicate,
    jaccard,
    token_set,
)

ROOT = Path(__file__).resolve().parents[2]


def load_events() -> list[NormalizedEvent]:
    with (ROOT / "data" / "news" / "synthetic_raw.jsonl").open(encoding="utf-8") as handle:
        return [NormalizedEvent.model_validate_json(line) for line in handle if line.strip()]


def test_normalization_helpers():
    assert canonical_title("  ЦБ РФ: ставка — 16%!  ") == "цб рф ставка 16"
    assert "ставка" in token_set("Ключевая ставка Банка России")
    assert jaccard({"ставка", "цб"}, {"ставка", "цб"}) == 1.0
    assert jaccard(set(), {"a"}) == 0.0


def test_dedupe_synthetic_set_removes_exact_duplicate():
    events = load_events()
    result = dedupe_events(events, threshold=0.88)
    assert len(events) == 25
    assert len(result.unique) == 23
    assert result.duplicates["news:syn-024"] == "news:syn-001"
    assert result.duplicates["news:syn-025"] == "news:syn-004"
    duplicate, score = find_duplicate(events[0], events, threshold=0.99)
    assert duplicate is not None
    assert score == pytest.approx(1.0)
    assert event_similarity(events[0], events[1]) < 1.0


def test_extract_event_from_text():
    text = (
        "Банк России сохранил ключевую ставку на уровне 16% годовых. "
        "Инфляция замедляется медленнее ожиданий, рубль ослаб до 95 за доллар."
    )
    event = extract_event(text, catalog=None)
    assert event.event_type.value in {"MONETARY_POLICY", "FX"}
    assert any(factor.value in {"KEY_RATE", "FX_RATE", "INFLATION"} for factor in event.macro_factors)
    assert "РОССИЯ" in event.countries
    assert event.source.source_id.startswith("news:")
    assert event.event_id == build_event_id(f"{event.title}. {text}")
    assert 0.0 <= event.noise_score <= 1.0


def test_extract_speculation_and_noise():
    text = (
        "СРОЧНО! По данным источников, ЦБ может внепланово снизить ставку. "
        "Официального подтверждения нет, слухи обсуждают в соцсетях!!!"
    )
    event = extract_event(text)
    assert event.is_speculation is True
    assert event.noise_score > 0.4
    assert event.confidence < 0.6
    assert detect_event_type(text).value == "MONETARY_POLICY"
    assert detect_countries(text) == []
    assert detect_macro_factors(text)


def test_html_and_rss_extraction():
    html_payload = (
        "<html><head><title>Заголовок</title>"
        "<meta name='description' content='Описание'></head>"
        "<body><script>ignore()</script><p>Первый абзац.</p><p>Второй абзац.</p></body></html>"
    )
    title, description, text = extract_text_from_html(html_payload)
    assert title == "Заголовок"
    assert description == "Описание"
    assert "Первый абзац" in text
    assert "ignore" not in text

    rss_payload = """<?xml version="1.0"?>
    <rss version="2.0"><channel><title>Test RSS</title>
    <item><title>Новость</title><description><![CDATA[<p>Текст</p>]]></description>
    <link>https://example.com/1</link><pubDate>Wed, 21 Oct 2026 09:00:00 +0300</pubDate></item>
    </channel></rss>"""
    items = parse_rss(rss_payload)
    assert len(items) == 1
    assert items[0]["title"] == "Новость"
    assert items[0]["summary"] == "Текст"
    assert items[0]["source_name"] == "Test RSS"


def test_url_validation_blocks_private_hosts():
    assert validate_public_url("https://93.184.216.34/news") == "https://93.184.216.34/news"
    with pytest.raises(ValueError):
        validate_public_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        validate_public_url("http://localhost:8000")
    with pytest.raises(ValueError):
        validate_public_url("http://10.0.0.1/internal")


def test_ingest_service_and_duplicate(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path,
        scoring_config=ROOT / "config" / "scoring.yaml",
        industries_config=ROOT / "config" / "industries.yaml",
        llm_config=ROOT / "config" / "llm.yaml",
        llm_enabled=False,
    )
    store = DataStore(
        settings,
        companies_path=tmp_path / "companies.parquet",
        graph_path=tmp_path / "graph_features.parquet",
        news_path=tmp_path / "news" / "events.jsonl",
    )
    payload = (
        "Правительство расширило поддержку IT-компаний: новые льготы касаются "
        "налога на прибыль и доступа к льготному финансированию."
    )
    first = ingest_event(store, settings, text=payload)
    assert first.duplicate_of is None
    assert first.event.event_id.startswith("news:")
    assert store.news_path.exists()

    second = ingest_event(store, settings, text=payload)
    assert second.duplicate_of == first.event.event_id
    assert second.event.event_id == first.event.event_id
    assert len(store.events_or_empty()) == 1
