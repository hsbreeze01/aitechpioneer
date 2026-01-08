from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str = ""

    log_level: str = "INFO"
    debug: bool = False

    app_name: str = "aitechpioneer"
    app_version: str = "0.1.0"


settings = Settings()
