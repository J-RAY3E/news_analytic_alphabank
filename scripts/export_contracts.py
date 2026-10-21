import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.contracts.models import (  # noqa: E402
    EvidenceClaim,
    Insight,
    NormalizedEvent,
    TraceEvent,
)

SCHEMA_DIR = ROOT / "contracts" / "schemas"

SCHEMAS = {
    "normalized_event": NormalizedEvent,
    "evidence_claim": EvidenceClaim,
    "agent_trace": TraceEvent,
    "insight": Insight,
}


def main() -> None:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for name, model in SCHEMAS.items():
        target = SCHEMA_DIR / f"{name}.schema.json"
        target.write_text(
            json.dumps(model.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
