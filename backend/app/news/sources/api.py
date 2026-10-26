from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from app.news.sources.base import HttpClient, RawItem, Source

CBR_DAILY_URL = "https://www.cbr.ru/currency_base/daily/"
CBR_WANTED = {"USD", "EUR", "CNY"}


def fetch(source: Source, http: HttpClient, limit: int = 10) -> list[RawItem]:
    if source.api == "moex_iss":
        return _fetch_moex(source, http, limit)
    if source.api == "cbr_fx":
        return _fetch_cbr(source, http, limit)
    return []


def _fetch_moex(source: Source, http: HttpClient, limit: int) -> list[RawItem]:
    if not source.url:
        return []
    content = http.get_bytes(source.url, source.rate_limit_per_minute)
    payload = json.loads(content.decode("utf-8", "replace"))
    securities = payload.get("securities", {})
    marketdata = payload.get("marketdata", {})

    names: dict[str, str] = {}
    sec_columns = securities.get("columns") or []
    if "SECID" in sec_columns:
        secid_at = sec_columns.index("SECID")
        name_at = sec_columns.index("SHORTNAME") if "SHORTNAME" in sec_columns else secid_at
        for row in securities.get("data") or []:
            names[row[secid_at]] = row[name_at]

    prices: dict[str, object] = {}
    md_columns = marketdata.get("columns") or []
    if "SECID" in md_columns and "LAST" in md_columns:
        secid_at = md_columns.index("SECID")
        last_at = md_columns.index("LAST")
        for row in marketdata.get("data") or []:
            prices[row[secid_at]] = row[last_at]

    now = datetime.now(timezone.utc)
    items: list[RawItem] = []
    for secid, last in prices.items():
        if last is None:
            continue
        if len(items) >= max(limit, 0):
            break
        name = names.get(secid, secid)
        items.append(
            RawItem(
                title=f"MOEX: {name} ({secid}) — {last}",
                summary=(
                    f"Последняя цена {name} на Московской бирже: {last}. "
                    "Источник: официальный ISS API Московской биржи."
                ),
                url="https://www.moex.com/",
                source_name=source.name,
                source_id=f"{source.id}:{secid}",
                published_at=now,
                tags=source.tags,
            )
        )
    return items


def _fetch_cbr(source: Source, http: HttpClient, limit: int) -> list[RawItem]:
    if not source.url:
        return []
    content = http.get_bytes(source.url, source.rate_limit_per_minute)
    root = ET.fromstring(content.decode("windows-1251", "replace"))
    date_attr = root.get("Date")
    now = datetime.now(timezone.utc)
    items: list[RawItem] = []
    for valute in root.findall("Valute"):
        code = (valute.findtext("CharCode") or "").strip()
        if code not in CBR_WANTED:
            continue
        name = (valute.findtext("Name") or code).strip()
        value = (valute.findtext("Value") or "").strip()
        nominal = (valute.findtext("Nominal") or "1").strip()
        items.append(
            RawItem(
                title=f"Курс {name} (ЦБ РФ): {value} ₽",
                summary=(
                    f"Официальный курс Банка России: {nominal} {code} = {value} ₽"
                    + (f" на {date_attr}." if date_attr else ".")
                ),
                url=CBR_DAILY_URL,
                source_name=source.name,
                source_id=f"{source.id}:{code}:{date_attr}",
                published_at=now,
                tags=source.tags,
            )
        )
        if len(items) >= max(limit, 0):
            break
    return items
