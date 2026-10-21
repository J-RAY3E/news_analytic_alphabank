from __future__ import annotations

import hashlib
import html
import ipaddress
import re
import socket
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlparse

import httpx

from app.contracts import (
    EventType,
    Figure,
    MacroFactor,
    NormalizedEvent,
    RiskOpportunity,
    Sentiment,
    SourceRef,
)
from app.data.industries import IndustryCatalog, load_industry_catalog
from app.news.normalize import normalize_whitespace

USER_AGENT = "AlfaRadar/0.1 (+https://example.com/alfa-radar)"
MAX_FETCH_BYTES = 2_000_000

EVENT_KEYWORDS: dict[EventType, tuple[str, ...]] = {
    EventType.MONETARY_POLICY: ("ключев", "ставк", "банк россии", "цб", "денежно-кредит"),
    EventType.FX: ("рубл", "доллар", "евро", "курс", "валют"),
    EventType.REGULATION: ("маркировк", "регулир", "закон", "правительств", "требован", "квот"),
    EventType.SANCTIONS: ("санкц", "ограничен", "блокир", "запрет"),
    EventType.LOGISTICS: ("логист", "тариф", "перевоз", "таможн", "поставк", "экспорт", "импорт"),
    EventType.COMMODITIES: ("нефт", "алюмин", "металл", "сырь", "brent", "золот"),
    EventType.DEMAND: ("спрос", "потреб", "товарооборот", "экспорт"),
    EventType.COMPETITION: ("конкурент", "ритейлер", "расшир", "доля рынка"),
    EventType.TAX: ("налог", "фнс", "ндс", "отчетност", "декларац"),
    EventType.LABOR: ("зарплат", "кадр", "безработ", "сотрудник", "персонал"),
    EventType.TECHNOLOGY: ("ит-", "цифров", "технолог", "оборудован", "программ"),
}

MACRO_KEYWORDS: dict[MacroFactor, tuple[str, ...]] = {
    MacroFactor.KEY_RATE: ("ключев", "ставк"),
    MacroFactor.INFLATION: ("инфляц",),
    MacroFactor.FX_RATE: ("рубл", "доллар", "евро", "курс", "валют"),
    MacroFactor.BOND_YIELD: ("облигац", "доходност", "депозит"),
    MacroFactor.COMMODITY_PRICE: ("нефт", "алюмин", "металл", "сырь", "brent", "золот"),
    MacroFactor.DEMAND: ("спрос", "потреб", "товарооборот"),
    MacroFactor.SUPPLY_CHAIN: ("поставк", "логист", "таможн", "перевоз", "импорт", "экспорт", "дефицит"),
    MacroFactor.REGULATION: ("маркировк", "регулир", "закон", "правительств", "требован", "квот"),
    MacroFactor.TAX: ("налог", "фнс", "ндс"),
    MacroFactor.SANCTIONS: ("санкц", "блокир"),
    MacroFactor.LABOR_COST: ("зарплат", "кадр", "безработ"),
    MacroFactor.CREDIT_ACCESS: ("кредит", "гаранти", "заем", "лизинг"),
}

COUNTRY_KEYWORDS: dict[str, str] = {
    "китай": "КИТАЙ",
    "турци": "ТУРЦИЯ",
    "инди": "ИНДИЯ",
    "росси": "РОССИЯ",
    "оаэ": "ОАЭ",
    "гонконг": "ГОНКОНГ",
    "литв": "ЛИТВА",
    "узбек": "УЗБЕКИСТАН",
}

REGION_KEYWORDS: dict[str, str] = {
    "москв": "Москва",
    "санкт-петербург": "Санкт-Петербург",
    "петербург": "Санкт-Петербург",
    "новосибирск": "Новосибирская область",
    "свердловск": "Свердловская область",
    "екатеринбург": "Свердловская область",
    "татарстан": "Республика Татарстан",
    "казан": "Республика Татарстан",
    "краснодар": "Краснодарский край",
    "челябинск": "Челябинская область",
    "нижегород": "Нижегородская область",
    "красноярск": "Красноярский край",
    "ростов": "Ростовская область",
    "башкорт": "Башкортостан (Республика)",
    "иркутск": "Иркутская область",
    "примор": "Приморский край",
}

POSITIVE_WORDS = ("рост", "вырос", "увелич", "поддерж", "льгот", "упростил", "снижен", "выигр")
NEGATIVE_WORDS = ("снизил", "упал", "подешев", "риск", "угроз", "ужесточ", "дефицит", "санкц", "огранич")
SPECULATION_WORDS = (
    "слух",
    "по данным источников",
    "источники сообщ",
    "может",
    "вероятно",
    "обсужда",
    "не подтвержд",
    "не комментирует",
)
NOISE_WORDS = ("шок", "срочно", "эксклюзив", "вы не поверите", "сенсац")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self._in_title = False
        self._skip = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "nav", "footer"}:
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            attributes = dict(attrs)
            if attributes.get("name") in {"description", "og:description"}:
                self.description = html.unescape(attributes.get("content") or "")
        elif tag in {"p", "br", "div", "li", "h1", "h2", "h3"} and not self._skip:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "nav", "footer"} and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = html.unescape(data)
        if self._in_title:
            self.title += text
        elif not self._skip:
            self._chunks.append(text)

    @property
    def text(self) -> str:
        return normalize_whitespace(" ".join(self._chunks))


def extract_text_from_html(payload: str) -> tuple[str, str, str]:
    parser = PageParser()
    parser.feed(payload)
    return (
        normalize_whitespace(parser.title),
        normalize_whitespace(parser.description),
        parser.text,
    )


def validate_public_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("url must be http(s) with a hostname")
    host = parsed.hostname.casefold()
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("private hosts are not allowed")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        addresses = [
            ipaddress.ip_address(item[4][0])
            for item in socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        ]
    for address in addresses:
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
            or address.is_multicast
            or address.is_unspecified
        ):
            raise ValueError("private network addresses are not allowed")
    return url


def fetch_url(url: str, timeout: float = 10.0) -> tuple[str, str, str, str]:
    validate_public_url(url)
    with httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        payload = response.text[:MAX_FETCH_BYTES]
    title, description, text = extract_text_from_html(payload)
    return title, description, text, str(response.url)


def parse_rss(xml_payload: str) -> list[dict[str, Any]]:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_payload)
    items: list[dict[str, Any]] = []
    atom = "{http://www.w3.org/2005/Atom}"
    if root.tag.endswith("feed"):
        source_title = normalize_whitespace(
            (root.findtext(f"{atom}title") or "")
        )
        for entry in root.findall(f"{atom}entry"):
            link = ""
            for link_element in entry.findall(f"{atom}link"):
                if link_element.get("rel") in {None, "alternate"}:
                    link = link_element.get("href") or ""
                    break
            summary = entry.findtext(f"{atom}summary") or entry.findtext(f"{atom}content") or ""
            items.append(
                {
                    "title": normalize_whitespace(entry.findtext(f"{atom}title") or ""),
                    "summary": strip_html(summary),
                    "url": link,
                    "published_at": entry.findtext(f"{atom}updated")
                    or entry.findtext(f"{atom}published"),
                    "source_name": source_title,
                }
            )
        return items

    channel = root.find("channel")
    source_title = normalize_whitespace(channel.findtext("title") or "") if channel is not None else ""
    for item in root.iter("item"):
        items.append(
            {
                "title": normalize_whitespace(item.findtext("title") or ""),
                "summary": strip_html(item.findtext("description") or ""),
                "url": normalize_whitespace(item.findtext("link") or ""),
                "published_at": item.findtext("pubDate"),
                "source_name": source_title,
            }
        )
    return items


def strip_html(payload: str) -> str:
    return normalize_whitespace(re.sub(r"<[^>]+>", " ", html.unescape(payload)))


def _match_any(text: str, keywords: tuple[str, ...] | list[str]) -> bool:
    lowered = text.casefold()
    return any(keyword.casefold() in lowered for keyword in keywords)


def detect_event_type(text: str) -> EventType:
    scores: dict[EventType, int] = {}
    for event_type, keywords in EVENT_KEYWORDS.items():
        score = sum(text.casefold().count(keyword.casefold()) for keyword in keywords)
        if score:
            scores[event_type] = score
    if not scores:
        return EventType.OTHER
    return max(scores, key=scores.get)


def detect_macro_factors(text: str) -> list[MacroFactor]:
    lowered = text.casefold()
    found = [
        factor
        for factor, keywords in MACRO_KEYWORDS.items()
        if any(keyword in lowered for keyword in keywords)
    ]
    return found


def detect_countries(text: str) -> list[str]:
    lowered = text.casefold()
    countries = [name for key, name in COUNTRY_KEYWORDS.items() if key in lowered]
    return list(dict.fromkeys(countries))


def detect_regions(text: str) -> list[str]:
    lowered = text.casefold()
    regions = [name for key, name in REGION_KEYWORDS.items() if key in lowered]
    return list(dict.fromkeys(regions))


def detect_sentiment(text: str) -> Sentiment:
    lowered = text.casefold()
    positive = sum(word in lowered for word in POSITIVE_WORDS)
    negative = sum(word in lowered for word in NEGATIVE_WORDS)
    if positive and negative:
        return Sentiment.MIXED
    if positive:
        return Sentiment.POSITIVE
    if negative:
        return Sentiment.NEGATIVE
    return Sentiment.NEUTRAL


def detect_risk_opportunity(sentiment: Sentiment) -> RiskOpportunity:
    return {
        Sentiment.POSITIVE: RiskOpportunity.OPPORTUNITY,
        Sentiment.NEGATIVE: RiskOpportunity.RISK,
        Sentiment.MIXED: RiskOpportunity.BOTH,
        Sentiment.NEUTRAL: RiskOpportunity.NEUTRAL,
    }[sentiment]


def detect_figures(text: str) -> list[Figure]:
    figures: list[Figure] = []
    for match in re.finditer(r"(\d+(?:[.,]\d+)?)\s*%", text):
        figures.append(
            Figure(label="Доля", value=float(match.group(1).replace(",", ".")), unit="%")
        )
    for match in re.finditer(
        r"(\d+(?:[.,]\d+)?)\s*(млрд|млн|трлн)?\s*(?:руб|₽)", text, flags=re.IGNORECASE
    ):
        unit = (match.group(2) or "руб").casefold()
        figures.append(
            Figure(
                label="Сумма",
                value=float(match.group(1).replace(",", ".")),
                unit=unit,
            )
        )
    for match in re.finditer(
        r"(\d+(?:[.,]\d+)?)\s*(доллар|usd|евро|eur)", text, flags=re.IGNORECASE
    ):
        figures.append(
            Figure(
                label="Курс",
                value=float(match.group(1).replace(",", ".")),
                unit=match.group(2).upper(),
            )
        )
    return figures[:10]


def estimate_noise(text: str) -> float:
    if not text:
        return 0.5
    letters = [character for character in text if character.isalpha()]
    upper_ratio = (
        sum(character.isupper() for character in letters) / len(letters) if letters else 0.0
    )
    noise = 0.0
    noise += min(upper_ratio, 0.6) * 0.5
    noise += min(text.count("!"), 5) * 0.04
    if len(text) < 120:
        noise += 0.2
    if _match_any(text, NOISE_WORDS):
        noise += 0.3
    return round(min(noise, 1.0), 3)


def build_event_id(text: str) -> str:
    digest = hashlib.sha256(normalize_whitespace(text).casefold().encode("utf-8")).hexdigest()
    return f"news:{digest[:16]}"


def extract_event(
    text: str,
    title: str | None = None,
    source_url: str | None = None,
    source_name: str | None = None,
    published_at: datetime | None = None,
    summary: str = "",
    catalog: IndustryCatalog | None = None,
) -> NormalizedEvent:
    catalog = catalog or load_industry_catalog("config/industries.yaml")
    cleaned = normalize_whitespace(text)
    if not cleaned:
        raise ValueError("text is empty")
    resolved_title = normalize_whitespace(title or cleaned.split(".")[0][:200])
    if len(resolved_title) < 3:
        resolved_title = cleaned[:200]
    combined = f"{resolved_title}. {cleaned}"
    event_type = detect_event_type(combined)
    macro_factors = detect_macro_factors(combined)
    sections = catalog.infer_sections_from_text(combined)
    sectors = sections or ["ALL"]
    countries = detect_countries(combined) or ["РОССИЯ"]
    regions = detect_regions(combined)
    sentiment = detect_sentiment(combined)
    noise = estimate_noise(cleaned)
    speculation = _match_any(combined, SPECULATION_WORDS)
    confidence = 0.6 - noise * 0.25 - (0.2 if speculation else 0.0)
    confidence = round(max(0.1, min(confidence, 0.85)), 3)
    normalized = normalize_whitespace(summary or cleaned[:500])
    return NormalizedEvent(
        event_id=build_event_id(combined),
        title=resolved_title,
        summary=normalized[:4000],
        raw_text=cleaned[:100_000],
        event_type=event_type,
        sectors=sectors,
        regions=regions,
        countries=countries,
        macro_factors=macro_factors,
        entities=[],
        figures=detect_figures(cleaned),
        sentiment=sentiment,
        risk_opportunity=detect_risk_opportunity(sentiment),
        is_speculation=speculation,
        noise_score=noise,
        confidence=confidence,
        source=SourceRef(
            source_id=build_event_id(combined),
            name=source_name or (urlparse(source_url).hostname if source_url else "User Input"),
            url=source_url,
            published_at=published_at or datetime.now(timezone.utc),
            language="ru",
        ),
    )
