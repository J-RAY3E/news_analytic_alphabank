import json
from pathlib import Path

import pandas as pd
import pytest

from app.data.exposure import build_graph_features, build_payment_edges


def companies_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "company_id": "U_1",
                "okved_division": "46",
                "okved_section": "G",
                "industry_label": "Торговля оптовая и розничная",
                "group_id": "g1",
            },
            {
                "company_id": "U_2",
                "okved_division": "41",
                "okved_section": "F",
                "industry_label": "Строительство",
                "group_id": "g1",
            },
            {
                "company_id": "U_3",
                "okved_division": "64",
                "okved_section": "K",
                "industry_label": "Финансы",
                "group_id": "g2",
            },
            {
                "company_id": "U_4",
                "okved_division": "46",
                "okved_section": "G",
                "industry_label": "Торговля оптовая и розничная",
                "group_id": "g2",
            },
        ]
    )


def payments_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"PAYER": "U_1", "BENEFICIARY": "U_2", "PAY_AMT": 100.0, "PAY_CNT": 2},
            {"PAYER": "U_1", "BENEFICIARY": "U_2", "PAY_AMT": 50.0, "PAY_CNT": 1},
            {"PAYER": "U_1", "BENEFICIARY": "U_3", "PAY_AMT": 50.0, "PAY_CNT": 1},
            {"PAYER": "U_2", "BENEFICIARY": "U_1", "PAY_AMT": 20.0, "PAY_CNT": 1},
            {"PAYER": "U_1", "BENEFICIARY": "U_1", "PAY_AMT": 999.0, "PAY_CNT": 1},
            {"PAYER": "U_5", "BENEFICIARY": "U_1", "PAY_AMT": 30.0, "PAY_CNT": 1},
            {"PAYER": "U_1", "BENEFICIARY": "U_6", "PAY_AMT": 10.0, "PAY_CNT": 1},
        ]
    )


def test_payment_edges_aggregate_and_remove_self_loops():
    edges = build_payment_edges(payments_frame())
    assert len(edges) == 5
    assert not ((edges["payer_id"] == "U_1") & (edges["beneficiary_id"] == "U_1")).any()
    row = edges[(edges["payer_id"] == "U_1") & (edges["beneficiary_id"] == "U_2")].iloc[0]
    assert row["amount"] == 150.0
    assert row["payment_count"] == 3


def test_graph_features_shares_and_group_exposure():
    result = build_graph_features(companies_frame(), payments_frame())
    frame = result.features.set_index("company_id")
    u1 = frame.loc["U_1"]
    assert bool(u1["has_payment_activity"]) is True
    supplier = json.loads(u1["supplier_division_shares"])
    client = json.loads(u1["client_division_shares"])
    assert sum(supplier.values()) == pytest.approx(1.0)
    assert sum(client.values()) == pytest.approx(1.0)
    # Intra-group transfers (U_1 <-> U_2, same group g1) are excluded from shares.
    assert "41" not in supplier
    assert supplier["64"] == pytest.approx(round(50 / 60, 6))
    assert supplier["UNKNOWN"] == pytest.approx(round(10 / 60, 6))
    assert client["UNKNOWN"] == pytest.approx(1.0)
    # Intra-group metric still reflects the excluded volume.
    assert u1["supplier_intra_group_share"] == pytest.approx(150 / 210)
    assert u1["client_intra_group_share"] == pytest.approx(0.4)
    assert u1["supplier_unique_counterparties"] == 3
    top = json.loads(u1["supplier_top_industries"])
    assert top[0]["division"] == "64"
    assert top[0]["share"] == pytest.approx(round(50 / 60, 6))

    u4 = frame.loc["U_4"]
    assert bool(u4["has_payment_activity"]) is False
    assert json.loads(u4["supplier_division_shares"]) == {}
    assert result.quality["companies_with_payment_activity"] == 3
    assert result.quality["intra_group_edges_excluded"] >= 1
