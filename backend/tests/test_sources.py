from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.contracts import MacroFactor
from app.data.industries import load_industry_catalog
from app.news.sources import api, rss, scrape
from app.news.sources.base import RawItem, Source, load_sources

ROOT = Path(__file__).resolve().parents[2]

RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>ЦБ сохранил ключевую ставку</title>
      <description>Регулятор оставил ставку без изменений.</description>
      <link>https://example.com/a</link>
      <pubDate>Tue, 14 Oct 2026 09:00:00 +0300</pubDate>
    </item>
    <item>
      <title></title>
      <link>https://example.com/b</link>
    </item>
  </channel>
</rss>
"""

MOEX_FIXTURE = (
    '{"securities":{"columns":["SECID","SHORTNAME"],'
    '"data":[["SBER","Сбербанк"],["GAZP","Газпром"],["LKOH","ЛУКОЙЛ"]]},'
    '"marketdata":{"columns":["SECID","LAST"],'
    '"data":[["SBER",312.4],["GAZP",null],["LKOH",6540.0]]}}'
)

CBR_FIXTURE = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="14.10.2026" name="Foreign Currency Market">
  <Valute ID="R01235">
    <NumCode>840</NumCode><CharCode>USD</CharCode><Nominal>1</Nominal>
    <Name>Доллар США</Name><Value>78,5000</Value>
  </Valute>
  <Valute ID="R01239">
    <NumCode>978</NumCode><CharCode>EUR</CharCode><Nominal>1</Nominal>
    <Name>Евро</Name><Value>91,2000</Value>
  </Valute>
  <Valute ID="R01375">
    <NumCode>156</NumCode><CharCode>CNY</CharCode><Nominal>1</Nominal>
    <Name>Китайский юань</Name><Value>10,9000</Value>
  </Valute>
</ValCurs>"""


class StubHttp:
    def __init__(self, mapping: dict[str, bytes]) -> None:
        self.mapping = mapping
        self.requests: list[str] = []

    def get_bytes(self, url: str, rate_limit_per_minute: int = 30) -> bytes:
        self.requests.append(url)
        return self.mapping[url]

    def allowed_by_robots(self, url: str) -> bool:
        return True


def test_load_sources_registry():
    sources = load_sources(ROOT / "config" / "news_sources.yaml")
    ids = {source.id for source in sources}
    assert {"moex_iss", "cbr_fx", "tass", "kommersant"} <= ids
    tass = next(source for source in sources if source.id == "tass")
    assert tass.kind == "rss"
    assert tass.url.startswith("https://")
    assert all(source.kind in {"rss", "api", "scrape"} for source in sources)


def test_rss_adapter_parses_and_skips_empty():
    source = Source(id="test", name="Test Feed", kind="rss", url="https://feed.test/rss")
    http = StubHttp({"https://feed.test/rss": RSS_FIXTURE.encode("utf-8")})
    items = rss.fetch(source, http, limit=10)
    assert len(items) == 1
    item = items[0]
    assert item.title == "ЦБ сохранил ключевую ставку"
    assert item.url == "https://example.com/a"
    assert item.published_at is not None
    assert item.published_at.year == 2026


def test_moex_api_adapter():
    source = Source(
        id="moex_iss", name="MOEX", kind="api", api="moex_iss", url="https://moex.test/iss"
    )
    http = StubHttp({"https://moex.test/iss": MOEX_FIXTURE.encode("utf-8")})
    items = api.fetch(source, http, limit=10)
    assert [item.source_id for item in items] == ["moex_iss:SBER", "moex_iss:LKOH"]
    assert "SBER" in items[0].title


def test_cbr_api_adapter_windows_1251():
    source = Source(
        id="cbr_fx", name="ЦБ РФ", kind="api", api="cbr_fx", url="https://cbr.test/daily"
    )
    http = StubHttp({"https://cbr.test/daily": CBR_FIXTURE.encode("windows-1251")})
    items = api.fetch(source, http, limit=10)
    codes = {item.source_id.split(":")[1] for item in items}
    assert codes == {"USD", "EUR", "CNY"}
    assert "Доллар США" in items[0].title


def test_scrape_adapter_extract_links():
    html = (
        '<html><body>'
        '<a href="/news/1">Очень важная новость про ставку</a>'
        '<a href="/about">О нас</a>'
        '</body></html>'
    )
    links = scrape.extract_links(html)
    assert ("/news/1", "Очень важная новость про ставку") in links


def test_raw_to_event_applies_default_macro():
    from app.news.sources.convert import raw_to_event

    catalog = load_industry_catalog(str(ROOT / "config" / "industries.yaml"))
    item = RawItem(
        title="MOEX: TEST (TEST) — 100",
        summary="Последняя цена TEST.",
        url="https://example.com/moex",
        source_name="MOEX",
        source_id="moex_iss:TEST",
        published_at=datetime.now(timezone.utc),
        tags={"default_macro": ["BOND_YIELD"]},
    )
    event = raw_to_event(item, catalog)
    assert MacroFactor.BOND_YIELD in event.macro_factors
    assert event.event_id.startswith("news:")


def test_dedupe_identical_items():
    from app.news.normalize import find_duplicate

    item = RawItem(
        title="Рубль ослаб до 95 за доллар",
        summary="Курс рубля снизился на фоне оттока капитала.",
        url="https://example.com/fx",
        source_name="Test",
        source_id="test:fx",
    )
    catalog = load_industry_catalog(str(ROOT / "config" / "industries.yaml"))
    from app.news.sources.convert import raw_to_event

    first = raw_to_event(item, catalog)
    second = raw_to_event(item, catalog)
    duplicate, score = find_duplicate(second, [first])
    assert duplicate is not None
    assert score >= 0.88
