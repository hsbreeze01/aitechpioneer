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

    deepseek_api_key: str = ""

    siliconflow_api_key: str = ""
    embedding_model: str = "BAAI/bge-large-zh-v1.5"
    embedding_api_url: str = "https://api.siliconflow.cn/v1/embeddings"
    
    use_local_embedding: bool = True
    local_embedding_model: str = "BAAI/bge-small-zh-v1.5"

    log_level: str = "INFO"
    debug: bool = False

    app_name: str = "aitechpioneer"
    app_version: str = "0.1.0"


settings = Settings()
