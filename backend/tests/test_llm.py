from pathlib import Path

import pytest

from app.config import Settings
from app.llm.client import LLMClient, LLMError
from app.llm.config import load_llm_config
from app.llm.governor import BudgetExceeded, CostGovernor

ROOT = Path(__file__).resolve().parents[2]


def test_llm_config_has_valid_routing():
    config = load_llm_config(ROOT / "config" / "llm.yaml")
    assert config.routing["reasoning"] in config.models
    assert config.routing["extraction"] in config.models
    assert config.daily_budget_rub == 500


def test_governor_blocks_over_budget(tmp_path: Path):
    config = load_llm_config(ROOT / "config" / "llm.yaml")
    governor = CostGovernor(config, tmp_path / "usage.jsonl")
    governor.record_usage(
        model="deepseek/deepseek-v4.1-flash",
        purpose="reasoning",
        prompt_tokens=1000,
        completion_tokens=1000,
        cost_rub=config.daily_budget_rub,
    )
    assert governor.spent_today() == pytest.approx(config.daily_budget_rub)
    assert governor.remaining() == 0
    with pytest.raises(BudgetExceeded):
        governor.check(0.01)


def test_llm_json_parser_accepts_fences_and_rejects_garbage():
    assert LLMClient._parse_json('```json\n{"ok": true}\n```') == {"ok": True}
    with pytest.raises(LLMError):
        LLMClient._parse_json("no json here")


def test_disabled_client_refuses_calls(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path,
        llm_config=ROOT / "config" / "llm.yaml",
        llm_enabled=False,
    )
    client = LLMClient(settings)
    assert client.enabled is False
    with pytest.raises(LLMError):
        client.complete_json(purpose="reasoning", system="s", user="u")


def test_llm_cache_reuses_response_without_second_call(tmp_path: Path, monkeypatch):
    from types import SimpleNamespace

    calls = {"count": 0}

    class FakeCompletions:
        def create(self, **kwargs):
            calls["count"] += 1
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content='{"status": "ok"}')
                    )
                ],
                usage=SimpleNamespace(
                    prompt_tokens=10, completion_tokens=5, cost=0.001
                ),
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.llm.client.OpenAI", FakeOpenAI)
    settings = Settings(
        data_dir=tmp_path,
        llm_config=ROOT / "config" / "llm.yaml",
        llm_enabled=True,
        llm_api_key="test-key",
    )
    client = LLMClient(settings)
    first = client.complete_json(purpose="reasoning", system="s", user="u")
    second = client.complete_json(purpose="reasoning", system="s", user="u")
    assert first == {"status": "ok"}
    assert second == {"status": "ok"}
    assert calls["count"] == 1
    assert client.last_usage["cached"] is True
    assert client.last_usage["prompt_tokens"] == 0
