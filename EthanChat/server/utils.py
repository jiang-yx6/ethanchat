from langchain_core.embeddings import Embeddings
from EthanChat.settings import Settings
from typing import Tuple
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