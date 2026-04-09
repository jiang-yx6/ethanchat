import os
from abc import ABC, abstractmethod
from pathlib import Path
import uuid
from typing import Dict, List, Optional, Tuple, Union
import chromadb

from langchain_core.documents.base import Document
from langchain_chroma import Chroma

from EthanChat.settings import Settings
from EthanChat.server.db.models.knowledge_base_model import KnowledgeBaseSchema
from EthanChat.server.db.repository.knowledge_base_repository import (
    add_kb_to_db,
    delete_kb_from_db,
    kb_exists,
    list_kbs_from_db,
    load_kb_from_db,
)

from EthanChat.server.db.repository.knowledge_file_repository import (
    add_file_to_db
)

# from EthanChat.server.db.repository.knowledge_file_repository import

from EthanChat.server.knowledge_base.utils import (
    KnowledgeFile,
    get_doc_path,
    get_kb_path,
    get_vs_path,
)

from EthanChat.server.utils import (
    get_default_embedding, 
    get_embedding_model,
    check_embed_model
)

class SuppprtedVSType:
    FAISS = "faiss"
    CHROMADB = "chromadb"
    MILVUS = "milvus"



class KBService(ABC):
    def __init__(self, kb_name: str, embed_model: str):
        self.kb_name = kb_name
        self.embed_model = embed_model
        self.kb_path = get_kb_path(self.kb_name)
        self.doc_path = get_doc_path(self.kb_name)
    
        # self.do_init()

    def add_doc(self, kb_file: KnowledgeFile):
        #加载文件
        if not check_embed_model(self.embed_model)[0]:
            return False

        docs = kb_file.file2docs_main()
        if docs:
            for doc in docs:
                try:
                    doc.metadata.setdefault("source", kb_file.filename)
                    source = doc.metadata.get("source", "")
                    if os.path.isabs(source):
                        rel_path = Path(source).relative_to(self.doc_path)
                        print("相对路径:",rel_path)
                        doc.metadata["source"] = str(rel_path.as_posix().strip("/"))
                except Exception as e:
                    print(
                        f"cannot convert absolute path ({source}) to relative path. error is : {e}"
                    )            
            #向量化 
            doc_infos = self.do_add_doc(docs)

            status = add_file_to_db(
                kb_file,
                doc_infos = doc_infos,
                docs_count = len(docs)
            )

        else:
            status = False
        return status
    
    def search_docs(self, 
                    query: str, 
                    topk: int = 5,
                    score_threshold: float = Settings.kb_settings.SCORE_THRESHOLD
                )->List[Document]:
        if not check_embed_model(self.embed_model)[0]:
            return []
        
        return self.do_search(query, topk, score_threshold)

    @abstractmethod
    def do_init(self): 
        pass

    @abstractmethod
    def do_add_doc(self, docs: List[Document]) -> List[Dict]: 
        pass

    @abstractmethod
    def do_search(
        self,
        query: str,
        tok_k: int,
        score_threshold: float,
    ) -> List[Tuple[Document, float]]:
        """
        搜索知识库
        """
        pass



class KBServiceFactory:
    @staticmethod
    def get_service(
        kb_name: str, 
        vs_type: str="chroma",
        embed_model : str = get_default_embedding()
    ):
        if vs_type == "chroma":
            return ChromaKBService(kb_name, embed_model)

        raise ValueError(f"不支持：{vs_type}")
    

class ChromaKBService(KBService):
    vs_path: str
    kb_path: str
    chorma: Chroma

    def do_init(self):
        self.vs_path = get_vs_path(self.kb_name, self.embed_model)

        self.client = chromadb.PersistentClient(path=self.vs_path)

        self.chroma = Chroma(
            client=self.client,
            collection_name=self.kb_name,
            embedding_function=get_embedding_model(self.embed_model)
        )

    def do_add_doc(self, docs: List[Document]):        
        ids = [str(uuid.uuid1()) for _ in range(len(docs))]
        metadatas = [doc.metadata for doc in docs]
        self.chroma.add_documents(
            ids=ids,
            documents=docs
        )
        doc_infos = [{"id": _id, "metadata":metadata} for _id, metadata in zip(ids,metadatas)]
        return doc_infos

    def do_search(
            self, query: str, top_k: int, score_thrshold:float= Settings.kb_settings.SCORE_THRESHOLD
    ) -> List[Tuple[Document, float]]:
        retriever = self.chroma.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": score_thrshold, "k": top_k}
        )

        docs = retriever.invoke(query)[:top_k]
        return docs


# if __name__ == '__main__':
#     service = KBServiceFactory.get_service(kb_name="medicine",vs_type="chroma")
#     print("成功获得chroma服务实例")
#     service.do_init()
#     print("成功初始化chroma")
#     # kb_file =  KnowledgeFile(
#     #     filename="1.病理生理学（第10版）.pdf",
#     #     kb_name="medicine"
#     # )
#     # print("成功构建PDF文件")
#     # service.add_doc(kb_file)
#     # print("成功加入知识库")
#     docs = service.search_docs("感冒可以吃火锅吗？",5, score_threshold=0.1)
    # print("查找成功")
    # for i in range(len(docs)):
    #
    #     print(f"============= 第 {i} 个文档 ===========\n")
    #
    #     print(docs[i])

