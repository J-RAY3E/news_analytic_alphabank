from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pandas as pd

UNKNOWN_DIVISION = "UNKNOWN"
UNKNOWN_SECTION = "UNKNOWN"
UNKNOWN_LABEL = "Неизвестная отрасль"


@dataclass(frozen=True)
class ExposureBuildResult:
    edges: pd.DataFrame
    features: pd.DataFrame
    quality: dict[str, Any]


def build_payment_edges(payments: pd.DataFrame) -> pd.DataFrame:
    edges = payments.rename(
        columns={
            "PAYER": "payer_id",
            "BENEFICIARY": "beneficiary_id",
            "PAY_AMT": "amount",
            "PAY_CNT": "payment_count",
        }
    ).copy()
    edges["payer_id"] = edges["payer_id"].astype(str).str.strip()
    edges["beneficiary_id"] = edges["beneficiary_id"].astype(str).str.strip()
    edges["amount"] = pd.to_numeric(edges["amount"], errors="coerce").fillna(0.0)
    edges["payment_count"] = (
        pd.to_numeric(edges["payment_count"], errors="coerce").fillna(0).astype("int64")
    )
    edges = edges[
        (edges["payer_id"] != "") & (edges["beneficiary_id"] != "") & (edges["amount"] > 0)
    ]
    edges = edges[edges["payer_id"] != edges["beneficiary_id"]]
    edges = (
        edges.groupby(["payer_id", "beneficiary_id"], as_index=False)
        .agg(amount=("amount", "sum"), payment_count=("payment_count", "sum"))
        .reset_index(drop=True)
    )
    return edges


def build_counterparty_map(companies: pd.DataFrame) -> pd.DataFrame:
    mapping = companies[
        ["company_id", "okved_division", "okved_section", "industry_label", "group_id"]
    ].copy()
    mapping["company_id"] = mapping["company_id"].astype(str)
    mapping["okved_division"] = mapping["okved_division"].fillna(UNKNOWN_DIVISION)
    mapping["okved_section"] = mapping["okved_section"].fillna(UNKNOWN_SECTION)
    mapping["industry_label"] = mapping["industry_label"].fillna(UNKNOWN_LABEL)
    mapping["group_id"] = mapping["group_id"].fillna("")
    return mapping.drop_duplicates(subset=["company_id"], keep="first")


def enrich_edges(edges: pd.DataFrame, counterparties: pd.DataFrame) -> pd.DataFrame:
    payer_map = counterparties.rename(
        columns={
            "company_id": "payer_id",
            "okved_division": "payer_division",
            "okved_section": "payer_section",
            "industry_label": "payer_industry_label",
            "group_id": "payer_group",
        }
    )
    beneficiary_map = counterparties.rename(
        columns={
            "company_id": "beneficiary_id",
            "okved_division": "beneficiary_division",
            "okved_section": "beneficiary_section",
            "industry_label": "beneficiary_industry_label",
            "group_id": "beneficiary_group",
        }
    )
    enriched = edges.merge(payer_map, on="payer_id", how="left").merge(
        beneficiary_map, on="beneficiary_id", how="left"
    )
    for column in ("payer_division", "payer_section", "beneficiary_division", "beneficiary_section"):
        enriched[column] = enriched[column].fillna(UNKNOWN_DIVISION if "division" in column else UNKNOWN_SECTION)
    for column in ("payer_industry_label", "beneficiary_industry_label"):
        enriched[column] = enriched[column].fillna(UNKNOWN_LABEL)
    for column in ("payer_group", "beneficiary_group"):
        enriched[column] = enriched[column].fillna("")
    return enriched


def _json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _side_features(
    edges: pd.DataFrame,
    company_ids: pd.Index,
    key: str,
    other: str,
    prefix: str,
    share_edges: pd.DataFrame | None = None,
) -> pd.DataFrame:
    key_prefix = key.removesuffix("_id")
    other_prefix = other.removesuffix("_id")
    subset = edges[edges[key].isin(company_ids)].copy()
    if subset.empty:
        return pd.DataFrame({"company_id": company_ids})
    # Industry shares, top counterparties and concentration exclude intra-group
    # transfers (case Q&A #21); totals and intra-group share keep the full subset.
    if share_edges is not None:
        share_source = share_edges[share_edges[key].isin(company_ids)].copy()
    else:
        share_source = subset

    total = subset.groupby(key).agg(
        total_amount=("amount", "sum"),
        total_payments=("payment_count", "sum"),
        unique_counterparties=(other, "nunique"),
    )
    total.index.name = "company_id"

    denominator = share_source.groupby(key)["amount"].transform("sum")
    share_source["_share"] = share_source["amount"] / denominator

    division = (
        share_source.groupby(
            [key, f"{other_prefix}_division", f"{other_prefix}_section"], as_index=False
        )
        .agg(amount=("amount", "sum"))
        .sort_values([key, "amount"], ascending=[True, False])
    )
    division["share"] = division["amount"] / division.groupby(key)["amount"].transform("sum")

    section = (
        share_source.groupby([key, f"{other_prefix}_section"], as_index=False)
        .agg(amount=("amount", "sum"))
        .sort_values([key, "amount"], ascending=[True, False])
    )
    section["share"] = section["amount"] / section.groupby(key)["amount"].transform("sum")

    labels = (
        share_source[
            [f"{other_prefix}_division", f"{other_prefix}_section", f"{other_prefix}_industry_label"]
        ]
        .drop_duplicates()
        .set_index([f"{other_prefix}_division", f"{other_prefix}_section"])
    )
    label_lookup = labels[f"{other_prefix}_industry_label"].to_dict()

    division_shares = {
        company: dict(zip(group[f"{other_prefix}_division"], group["share"].round(6)))
        for company, group in division.groupby(key)
    }
    section_shares = {
        company: dict(zip(group[f"{other_prefix}_section"], group["share"].round(6)))
        for company, group in section.groupby(key)
    }
    top_industries = {
        company: [
            {
                "division": row[f"{other_prefix}_division"],
                "section": row[f"{other_prefix}_section"],
                "industry_label": label_lookup.get(
                    (row[f"{other_prefix}_division"], row[f"{other_prefix}_section"]), UNKNOWN_LABEL
                ),
                "amount": float(row["amount"]),
                "share": round(float(row["share"]), 6),
            }
            for _, row in group.head(5).iterrows()
        ]
        for company, group in division.groupby(key)
    }

    counterparties = (
        share_source.groupby([key, other], as_index=False)
        .agg(amount=("amount", "sum"), payment_count=("payment_count", "sum"))
        .sort_values([key, "amount"], ascending=[True, False])
    )
    counterparty_meta = (
        share_source.groupby([key, other], as_index=False)[
            [f"{other_prefix}_division", f"{other_prefix}_section", f"{other_prefix}_industry_label"]
        ]
        .first()
    )
    counterparties = counterparties.merge(counterparty_meta, on=[key, other], how="left")
    counterparties["share"] = counterparties["amount"] / counterparties.groupby(key)[
        "amount"
    ].transform("sum")

    top_counterparties = {
        company: [
            {
                "counterparty_id": row[other],
                "amount": float(row["amount"]),
                "payment_count": int(row["payment_count"]),
                "division": row[f"{other_prefix}_division"],
                "section": row[f"{other_prefix}_section"],
                "industry_label": row[f"{other_prefix}_industry_label"],
            }
            for _, row in group.head(5).iterrows()
        ]
        for company, group in counterparties.groupby(key)
    }

    hhi = (
        counterparties.assign(squared=lambda frame: frame["share"] ** 2)
        .groupby(key)["squared"]
        .sum()
    )
    top1 = counterparties.groupby(key)["share"].max()
    top5 = (
        counterparties.sort_values([key, "share"], ascending=[True, False])
        .groupby(key)["share"]
        .apply(lambda series: float(series.head(5).sum()))
    )
    internal = subset[key_prefix + "_group"].ne("") & (
        subset[key_prefix + "_group"] == subset[other_prefix + "_group"]
    )
    internal_share = (
        subset.assign(_internal=internal)
        .groupby(key)
        .apply(
            lambda frame: float(frame.loc[frame["_internal"], "amount"].sum() / frame["amount"].sum())
            if frame["amount"].sum() > 0
            else 0.0,
            include_groups=False,
        )
    )

    result = pd.DataFrame(
        {
            "company_id": total.index,
            f"{prefix}_total_amount": total["total_amount"].values,
            f"{prefix}_total_payments": total["total_payments"].values,
            f"{prefix}_unique_counterparties": total["unique_counterparties"].values,
            f"{prefix}_division_shares": [_json(division_shares.get(company, {})) for company in total.index],
            f"{prefix}_section_shares": [_json(section_shares.get(company, {})) for company in total.index],
            f"{prefix}_top_industries": [_json(top_industries.get(company, [])) for company in total.index],
            f"{prefix}_top_counterparties": [_json(top_counterparties.get(company, [])) for company in total.index],
            f"{prefix}_hhi": [round(float(hhi.get(company, 0.0)), 6) for company in total.index],
            f"{prefix}_top1_share": [round(float(top1.get(company, 0.0)), 6) for company in total.index],
            f"{prefix}_top5_share": [round(float(top5.get(company, 0.0)), 6) for company in total.index],
            f"{prefix}_intra_group_share": [
                round(float(internal_share.get(company, 0.0)), 6) for company in total.index
            ],
        }
    )
    return result


def build_graph_features(
    companies: pd.DataFrame, payments: pd.DataFrame
) -> ExposureBuildResult:
    edges = build_payment_edges(payments)
    counterparties = build_counterparty_map(companies)
    enriched = enrich_edges(edges, counterparties)
    company_ids = pd.Index(companies["company_id"].astype(str).unique(), name="company_id")

    intra_group = (enriched["payer_group"] != "") & (
        enriched["payer_group"] == enriched["beneficiary_group"]
    )
    external = enriched[~intra_group]

    supplier_side = _side_features(
        enriched,
        company_ids=company_ids,
        key="payer_id",
        other="beneficiary_id",
        prefix="supplier",
        share_edges=external,
    )
    client_side = _side_features(
        enriched,
        company_ids=company_ids,
        key="beneficiary_id",
        other="payer_id",
        prefix="client",
        share_edges=external,
    )
    features = pd.DataFrame({"company_id": company_ids}).merge(
        supplier_side, on="company_id", how="left"
    ).merge(client_side, on="company_id", how="left")

    numeric_defaults = {
        "supplier_total_amount": 0.0,
        "supplier_total_payments": 0,
        "supplier_unique_counterparties": 0,
        "supplier_hhi": 0.0,
        "supplier_top1_share": 0.0,
        "supplier_top5_share": 0.0,
        "supplier_intra_group_share": 0.0,
        "client_total_amount": 0.0,
        "client_total_payments": 0,
        "client_unique_counterparties": 0,
        "client_hhi": 0.0,
        "client_top1_share": 0.0,
        "client_top5_share": 0.0,
        "client_intra_group_share": 0.0,
    }
    json_defaults = {
        "supplier_division_shares": "{}",
        "supplier_section_shares": "{}",
        "supplier_top_industries": "[]",
        "supplier_top_counterparties": "[]",
        "client_division_shares": "{}",
        "client_section_shares": "{}",
        "client_top_industries": "[]",
        "client_top_counterparties": "[]",
    }
    for column, value in {**numeric_defaults, **json_defaults}.items():
        if column not in features.columns:
            features[column] = value
        else:
            features[column] = features[column].fillna(value)
    for column in numeric_defaults:
        features[column] = pd.to_numeric(features[column], errors="coerce").fillna(0)
    features["total_payment_volume"] = (
        features["supplier_total_amount"] + features["client_total_amount"]
    )
    features["has_payment_activity"] = features["total_payment_volume"] > 0

    active = features["has_payment_activity"].sum()
    quality = {
        "payment_rows_raw": int(len(payments)),
        "edges_after_aggregation": int(len(edges)),
        "self_loops_removed": int(
            (
                payments.rename(columns={"PAYER": "p", "BENEFICIARY": "b"})["p"]
                == payments.rename(columns={"PAYER": "p", "BENEFICIARY": "b"})["b"]
            ).sum()
        ),
        "intra_group_edges_excluded": int(len(enriched) - len(external)),
        "companies_with_payment_activity": int(active),
        "coverage_share": round(float(active / len(features)), 6) if len(features) else 0.0,
        "known_counterparty_industry_share": round(
            float((enriched["beneficiary_section"] != UNKNOWN_SECTION).mean()), 6
        ),
    }
    return ExposureBuildResult(
        edges=enriched[
            [
                "payer_id",
                "beneficiary_id",
                "amount",
                "payment_count",
                "payer_division",
                "payer_section",
                "beneficiary_division",
                "beneficiary_section",
            ]
        ].reset_index(drop=True),
        features=features.reset_index(drop=True),
        quality=quality,
    )
