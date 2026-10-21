from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def scoring_path(project_root: Path) -> Path:
    return project_root / "config" / "scoring.yaml"


@pytest.fixture(scope="session")
def industries_path(project_root: Path) -> Path:
    return project_root / "config" / "industries.yaml"
