from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _resolve_project_path(value: Path) -> Path:
    return value if value.is_absolute() else PROJECT_ROOT / value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    data_dir: Path = PROJECT_ROOT / "data"
    scoring_config: Path = PROJECT_ROOT / "config" / "scoring.yaml"
    industries_config: Path = PROJECT_ROOT / "config" / "industries.yaml"
    llm_config: Path = PROJECT_ROOT / "config" / "llm.yaml"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    llm_enabled: bool = True
    llm_api_key: str = Field(default="", repr=False)
    llm_base_url: str = "https://api.alfahack-gateway26.ru/v1"
    llm_base_url_fallback: str = "https://changellenge.up.railway.app/v1"
    llm_daily_budget_rub: float = 500.0
    llm_model_extraction: str = "google/gemma-4-26b-a4b-it"
    llm_model_reasoning: str = "deepseek/deepseek-v4.1-flash"
    llm_model_fallback: str = "google/gemma-4-26b-a4b-it"
    llm_model_vision: str = "qwen/qwen3-vl-30b-a3b-instruct"
    llm_model_long: str = "moonshotai/kimi-k2.6"

    def model_post_init(self, __context: object) -> None:
        for name in ("scoring_config", "industries_config", "llm_config"):
            setattr(self, name, _resolve_project_path(getattr(self, name)))

    def path(self, *parts: str) -> Path:
        base = self.data_dir
        if not base.is_absolute():
            base = PROJECT_ROOT / base
        return base.joinpath(*parts)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
