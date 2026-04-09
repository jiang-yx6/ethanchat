import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 获取项目根目录
ROOT = Path(__file__).resolve().parent

class BasicSettings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SQLALCHEMY_DATABASE_URI: str = f"sqlite:///{ROOT}/data/knowledge_base/db.sqlite"
    KB_ROOT_PATH: str = str(ROOT / "data" / "knowledge_base")
    DB_ROOT_PATH: str = str("sqlite://" / ROOT / "data" / "knowledge_base/db.sqlite" )
    OPEN_CROSS_DOMAIN: bool = True

    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        extra="ignore",
        case_sensitive=True  # 环境变量通常区分大小写
    )


class KBSettings(BaseSettings):
    DEFAULT_VS_TYPE: str = "faiss"
    CHUNK_SIZE: int = 750
    OVERLAP_SIZE: int = 150
    SCORE_THRESHOLD: float = 0.4
    VECTOR_SEARCH_TOP_K: int = 5

    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        extra="ignore"
    )


class ModelSettings(BaseSettings):
    # DeepSeek 配置
    DEFAULT_LLM_MODEL: str = "deepseek-chat"
    DEFAULT_LLM_BASE_URL: str = "https://api.deepseek.com"
    LLM_API_KEY: str = "sk-b91af349394849dcbbcf44bdf7392a90"

    # 通义千问配置
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-v4"
    DEFAULT_EMBEDDING_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DASHSCOPE_API_KEY: str = "sk-7563a6ccdf3b4ebaa4777707bcd23bc3"

    # 通用参数
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048

    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        extra="ignore"
    )


class Settings:
    basic_settings = BasicSettings()
    kb_settings = KBSettings()
    model_settings = ModelSettings()


Settings = Settings()