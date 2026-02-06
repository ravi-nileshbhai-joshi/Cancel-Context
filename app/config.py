from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Cancel Context Collector"
    env: str = "dev"
    database_url: str = "sqlite:///./cancel_context.db"

    allow_auto_account: bool = True
    default_account_id: str = "demo"
    default_account_name: str = "Demo Account"
    default_founder_email: str = "founder@example.com"
    default_slack_webhook_url: Optional[str] = None
    default_account_api_key: Optional[str] = None

    cors_origins: str = "http://localhost:8000,http://localhost:3000"

    email_from: str = "no-reply@cancelcontext.local"
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True

    cancel_api_key: Optional[str] = None
    dashboard_api_key: Optional[str] = None

    allowed_reasons: str = "too_expensive,missing_feature,confusing,bug,no_longer_needed"

    cancel_rate_limit_per_minute: int = 30
    cancel_rate_limit_window_seconds: int = 60

    sentry_dsn: Optional[str] = None
    sentry_traces_sample_rate: float = 0.0

    redis_url: Optional[str] = None
    notification_queue_name: str = "notifications"
    notification_retry_intervals: str = "10,60,300"
    notification_max_attempts: int = 4

    auto_create_tables: bool = True
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def allowed_reason_list(self) -> List[str]:
        return [reason.strip() for reason in self.allowed_reasons.split(",") if reason.strip()]

    def notification_retry_interval_list(self) -> List[int]:
        intervals = []
        for value in self.notification_retry_intervals.split(","):
            value = value.strip()
            if not value:
                continue
            try:
                intervals.append(int(value))
            except ValueError:
                continue
        return intervals


settings = Settings()
