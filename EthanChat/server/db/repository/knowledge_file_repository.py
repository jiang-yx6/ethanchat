from typing import Dict, List

from EthanChat.server.db.models.knowledge_base_model import KnowledgeBaseModel
from EthanChat.server.db.models.knowledge_file_model import (
    FileDocModel,
    KnowledgeFileModel,
)
from EthanChat.server.db.session import with_session
# from EthanChat.server.knowledge_base.utils import KnowledgeFile

@with_session
def list_file_docs_id_by_kb_name_and_file_name(session,kb_name:str,file_name:str)->List[int]:
    """
    列出某个知识库中某个文件的所有Document的id
    返回：[int, int,...]
    """
    doc_ids = session.query(FileDocModel).filter_by(kb_name = kb_name, file_name=file_name).all()
    return [int(id[0]) for id in doc_ids]

@with_session
def list_docs_from_db(session, kb_name:str,file_name:str=None, metadata:Dict={}) -> List[Dict]:
    """
    列出某个知识库某文件对应的所有Document
    """