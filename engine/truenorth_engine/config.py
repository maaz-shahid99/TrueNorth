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

    # Jira Cloud connector (DF-1) for project go/no-go evidence. When base URL + token are
    # set and the request supplies inputs.jira_project, live issue signals are gathered;
    # otherwise the connector falls back to requester-supplied project facts.
    jira_base_url: str = ""
    jira_email: str = ""
    jira_token: str = ""
    # Optional JQL selecting the issues that represent strategic goals/OKRs (GA-1). When set
    # alongside the Jira credentials, those issues are pulled as goals for alignment scoring.
    jira_goal_jql: str = ""

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

    # Live model-call resilience (PL-1). The gateway owns its own retry loop, so the
    # SDK's built-in retries are disabled to avoid compounding backoff.
    model_timeout_seconds: float = 60.0
    model_max_retries: int = 3
    model_retry_base_delay: float = 1.0  # seconds; exponential backoff with jitter

    # Per-principal rate limit on the judgment endpoint, requests/minute (0 disables).
    rate_limit_per_minute: int = 60

    # Stakes tiers that require human sign-off before a decision counts as approved
    # (DI-7 / GV-2). Default: existential and executive decisions.
    review_required_tiers: list[StakesTier] = [StakesTier.S1, StakesTier.S2]

    # Google SSO (optional). When google_client_id and truenorth_jwt_secret are both set,
    # POST /v1/auth/google verifies a Google ID token and issues a TrueNorth session JWT.
    google_client_id: str = ""
    truenorth_jwt_secret: str = ""
    jwt_ttl_seconds: int = 3600
    sso_admin_emails: list[str] = []

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
