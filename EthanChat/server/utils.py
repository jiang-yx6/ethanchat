from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from EthanChat.settings import Settings
from typing import Tuple,Any,Optional,List,Callable
from pydantic import BaseModel,Field
def get_default_embedding():
    return Settings.model_settings.DEFAULT_EMBEDDING_MODEL

# def get_model_info(model_name: str, model_type: str):


def get_embedding_model(embed_model: str)->Embeddings:
    from langchain_community.embeddings import DashScopeEmbeddings
    embed_model = embed_model or get_default_embedding()
    api_key = Settings.model_settings.DASHSCOPE_API_KEY
    return DashScopeEmbeddings(
        model = embed_model,
        dashscope_api_key= api_key
    )


def check_embed_model(embed_model: str) -> Tuple[bool, str]:
    embed_model = embed_model or get_default_embedding()
    embeddings: Embeddings = get_embedding_model(embed_model)

    try:
        embeddings.embed_query("this is a test")
        return True,""
    except Exception as e:
        msg = f"failed to access embed model '{embed_model}': {e}"
        return False, msg         


def get_default_llm():
    return Settings.model_settings.DEFAULT_LLM_MODEL


def get_ChatOpenAI_llm(
        model_name: str = get_default_llm(),
        temperature: int = Settings.model_settings.TEMPERATURE,
        max_tokens: int = Settings.model_settings.MAX_TOKENS,
        streaming: bool = True, 
        callbacks: List[Callable] = [],
) -> ChatOpenAI:
    params = dict(
        model_name=model_name,
        temperature = temperature,
        max_tokens = max_tokens,
        streaming = streaming,
        callbacks = callbacks,
    )
    try:
        if Settings.model_settings.DEFAULT_LLM_BASE_URL:
            params.update(
                base_url=Settings.model_settings.DEFAULT_LLM_BASE_URL
            )
        if Settings.model_settings.LLM_API_KEY:
            params.update(
                api_key=Settings.model_settings.LLM_API_KEY
            )
        model = ChatOpenAI(**params)
    except Exception as e:
        print(f"failed to create ChatOpenAI for model: {model_name}.")
        model = None
    return model

def get_prompt_template(type: str, name: str) -> Optional[str]:
    """
    加载对应模板
    """
    return Settings.prompt_settings.model_dump().get(type,{}).get(name)

class BaseResponse(BaseModel):
    code: int = Field(200, description="API status code")
    msg: str = Field("success", description="API status message")
    data: Any = Field(None, description="API data")

    class Config:
        json_schema_extra = {
            "example":{
                "code":200,
                "msg": "success"
            }
        }