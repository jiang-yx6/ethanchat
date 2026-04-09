from typing import Dict, List

from EthanChat.server.db.models.knowledge_base_model import KnowledgeBaseModel
from EthanChat.server.db.models.knowledge_file_model import (
    FileDocModel,
    KnowledgeFileModel,
)
from EthanChat.server.db.session import with_session
from EthanChat.server.knowledge_base.utils import KnowledgeFile

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
    [{"id": str, "metadata": dict}, ...]
    """
    docs = session.query(FileDocModel).filter(FileDocModel.kb_name.ilike(kb_name))
    if file_name:
        docs = docs.filter(FileDocModel.file_name.ilike(file_name))
    for k, v in metadata.items():
        docs = docs.filter(FileDocModel.meta_data[k].as_string() == str(v))
    
    return [{"id": x.doc_id ,"metadata":x.metadata} for x in docs.all()]

@with_session
def delete_docs_from_db(
    session,
    kb_name: str,
    file_name: str = None,
) -> List[Dict]:
    """
    删除某知识库某文件对应的所有Document，并返回被删除的Document。
    返回形式：[{"id": str, "metadata": dict}, ...]
    """
    docs = list_docs_from_db(kb_name=kb_name, file_name=file_name)
    query = session.query(FileDocModel).filter(FileDocModel.kb_name.ilike(kb_name))
    if file_name:
        query = query.filter(FileDocModel.file_name.ilike(file_name))
    query.delete(synchronize_session=False)
    return docs

@with_session
def add_docs_to_db(session, kb_name: str, file_name: str, doc_infos: List[Dict]):
    """
    将某知识库某文件对应的所有Document信息添加到数据库。
    doc_infos形式：[{"id": str, "metadata": dict}, ...]
    """
    if doc_infos is None:
        print(
            "输入的server.db.repository.knowledge_file_repository.add_docs_to_db的doc_infos参数为None"
        )
        return False
    for d in doc_infos:
        obj = FileDocModel(
            kb_name=kb_name,
            file_name=file_name,
            doc_id=d["id"],
            meta_data=d["metadata"],
        )
        session.add(obj)
    return True


@with_session 
def add_file_to_db(
    session,
    kb_file: KnowledgeFile,
    docs_count: int,
    doc_infos: List[Dict]
):
    kb = session.query(KnowledgeBaseModel).filter_by(kb_name=kb_file.kb_name).first()
    if kb:
        existing_file: KnowledgeFileModel = (
            session.query(KnowledgeFileModel).filter(
                KnowledgeFileModel.kb_name.ilike(kb_file.kb_name),
                KnowledgeBaseModel.file_name.ilike(kb_file.filename),
            ).first()
        )
        mtime = kb_file.get_mtime()
        size = kb_file.get_size()

        if existing_file:
            existing_file.file_mtime = mtime
            existing_file.file_size = size
            existing_file.docs_count = docs_count
            existing_file.file_version += 1

        else:
            new_file = KnowledgeBaseModel(
                file_name=kb_file.filename,
                file_ext=kb_file.ext,
                kb_name=kb_file.kb_name,
                document_loader_name=kb_file.loader_name,
                text_splitter_name=kb_file.text_splitter_name or "SpacyTextSplitter",
                file_mtime=mtime,
                file_size=size,
                docs_count=docs_count,
            )
            kb.file_count += 11
            session.add(new_file)
        add_docs_to_db(
            kb_name=kb_file.kb_name, filename=kb_file.filename, doc_infos = doc_infos
        )
    return True