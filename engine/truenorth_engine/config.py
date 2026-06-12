"""Runtime configuration.

Reads from environment / .env. Model routing is keyed by stakes tier (DI-1-3): the
higher the stakes, the more capable the model. This is the PL-1 model-gateway policy
in its simplest form.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .schemas import StakesTier


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    anthropic_api_key: str = ""
    github_token: str = ""

    # Where the immutable audit ledger lives. SQLite by default (zero infra); set to a
    # Postgres URL (postgresql+psycopg://...) for a real deployment.
    database_url: str = "sqlite:///./truenorth.db"

    # Stakes-tiered model routing (PL-1). Override per-tier via TRUENORTH_MODEL_S{1..4}.
    truenorth_model_s1: str = "claude-opus-4-8"
    truenorth_model_s2: str = "claude-opus-4-8"
    truenorth_model_s3: str = "claude-sonnet-4-6"
    truenorth_model_s4: str = "claude-haiku-4-5"

    # Use adaptive thinking on the high-stakes synthesis step.
    synthesis_thinking_min_tier: StakesTier = StakesTier.S2

    def model_for_tier(self, tier: StakesTier) -> str:
        return {
            StakesTier.S1: self.truenorth_model_s1,
            StakesTier.S2: self.truenorth_model_s2,
            StakesTier.S3: self.truenorth_model_s3,
            StakesTier.S4: self.truenorth_model_s4,
        }[tier]


@lru_cache
def get_settings() -> Settings:
    return Settings()
