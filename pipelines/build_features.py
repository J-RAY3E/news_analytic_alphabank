#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

import pandas as pd  # noqa: E402

from app.data.exposure import build_graph_features  # noqa: E402
from app.data.industries import load_industry_catalog  # noqa: E402
from app.data.profiler import build_company_profiles  # noqa: E402
from app.scoring.config import load_scoring_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Alfa Radar entity features")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument(
        "--scoring", type=Path, default=ROOT / "config" / "scoring.yaml"
    )
    parser.add_argument(
        "--industries", type=Path, default=ROOT / "config" / "industries.yaml"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    companies_raw = pd.read_csv(args.raw_dir / "df_Uid_data_hack.csv", sep=";")
    payments_raw = pd.read_csv(args.raw_dir / "df_Uid_payment_hack.csv", sep=";")

    scoring = load_scoring_config(args.scoring)
    catalog = load_industry_catalog(args.industries)

    profile_result = build_company_profiles(companies_raw, catalog, scoring)
    companies = profile_result.companies
    companies.to_parquet(args.out_dir / "companies.parquet", index=False)

    exposure_result = build_graph_features(companies, payments_raw)
    exposure_result.features.to_parquet(args.out_dir / "graph_features.parquet", index=False)
    exposure_result.edges.to_parquet(args.out_dir / "payment_edges.parquet", index=False)

    quality = {
        "profile": profile_result.quality,
        "exposure": exposure_result.quality,
    }
    (args.out_dir / "quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"companies: {len(companies)}")
    print(f"target companies (>= 15bn RUB): {profile_result.quality['target_companies_revenue_ge_15bn']}")
    print(f"graph rows: {len(exposure_result.features)}")
    print(f"payment edges: {len(exposure_result.edges)}")
    print(f"wrote {args.out_dir / 'companies.parquet'}")
    print(f"wrote {args.out_dir / 'graph_features.parquet'}")
    print(f"wrote {args.out_dir / 'payment_edges.parquet'}")
    print(f"wrote {args.out_dir / 'quality_report.json'}")


if __name__ == "__main__":
    main()
