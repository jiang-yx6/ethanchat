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
    SCORE_THRESHOLD: float = 1.5
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


class PromptSettings(BaseSettings):
    """意图识别模板"""
    preprocess_model: dict = {
        "default": (
            "你只要回复0 和 1 ，代表不需要使用工具。以下几种问题不需要使用工具:\n"
            "1. 需要联网查询的内容\n"
            "2. 需要计算的内容\n"
            "3. 需要查询实时性的内容\n"
            "如果我的输入满足这几种情况，返回1。其他输入，请你回复0，你只要返回一个数字\n"
            "这是我的问题:"
            ),
    }

    """ LLM 通用模板 """
    llm_model: dict = {
        "default": "{{input}}",
        "with_history": (
            "The following is a friendly conversation between a human and an AI.\n"
            "The AI is talkative and provides lots of specific details from its context.\n"
            "If the AI does not know the answer to a question, it truthfully says it does not know.\n\n"
            "Current conversation:\n"
            "{{history}}\n"
            "Human: {{input}}\n"
            "AI:"
            ),
    }

    """RAG通用模板"""
    rag: dict = {
        "default": (
            "【指令】根据已知信息，简洁和专业的来回答问题。"
            "如果无法从中得到答案，请说 “根据已知信息无法回答该问题”，不允许在答案中添加编造成分，答案请使用中文。\n\n"
            "【已知信息】{{context}}\n\n"
            "【问题】{{question}}\n"
            ),
        "empty": (
            "请你回答我的问题:\n"
            "{{question}}"
        ),
    }


    action_model: dict = {
        "difault":{
              "SYSTEM_PROMPT": (
                "You are a helpful assistant"
            ),
            "HUMAN_MESSAGE": (
                "{input}"
            )
        },
        "deepseek":{
            "SYSTEM_PROMPT": (
                "请尽可能回答以下问题。你可以使用以下 API 工具：\n\n"
                "{tools}\n\n"
                "请严格遵循以下格式进行回复：\n\n"
                "Question: 你必须回答的输入问题\n"
                "Thought: 你应该始终思考接下来该做什么\n"
                "Action: 要采取的行动，必须是 [{tool_names}] 中的一个\n"
                "Action Input: 行动的输入参数\n"
                "Observation: 行动的结果\n"
                "... (这个 Thought/Action/Action Input/Observation 过程可以重复零次或多次)\n"
                "Thought: 我现在知道最终答案了\n"
                "Final Answer: 对原始输入问题的最终回答\n\n"
                "请将 Action Input 格式化为一个 JSON 对象。\n\n"
                "开始！\n\n"
            ),
            "HUMAN_MESSAGE": (
                "问题: {input}\n\n"
                "{agent_scratchpad}\n\n")
        },
    }
class Settings:
    basic_settings = BasicSettings()
    kb_settings = KBSettings()
    model_settings = ModelSettings()
    prompt_settings = PromptSettings()

Settings = Settings()