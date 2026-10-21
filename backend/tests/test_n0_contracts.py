import json
from pathlib import Path

from app.contracts import NormalizedEvent
from app.main import app

ROOT = Path(__file__).resolve().parents[2]


def test_openapi_export_is_current():
    exported = json.loads((ROOT / "contracts" / "openapi.json").read_text(encoding="utf-8"))
    assert exported == json.loads(json.dumps(app.openapi()))


def test_openapi_contains_n0_and_n2_contracts():
    paths = app.openapi()["paths"]
    for path in ("/health", "/companies", "/feed", "/events/{event_id}", "/insight"):
        assert path in paths
    insight = paths["/insight"]["post"]
    assert "200" in insight["responses"]
    assert insight["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "InsightRequest"
    )
    assert insight["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("InsightResponse")


def test_normalized_event_schema_export_is_current():
    exported = json.loads(
        (ROOT / "contracts" / "schemas" / "normalized_event.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert exported == NormalizedEvent.model_json_schema()
