import os
from EthanChat.settings import Settings
from pathlib import Path
import importlib

def get_kb_path(kb_name: str):
    return os.path.join(Settings.basic_settings.KB_ROOT_PATH, kb_name)

def get_vs_path(kb_name: str, vector_name: str):
    return os.path.join(get_kb_path(kb_name), "vector_store", vector_name)

def get_doc_path(kb_name: str):
    return os.path.join(get_kb_path(kb_name), "content")

def get_file_path(kb_name: str, file_name):
    kb_path = Path(get_doc_path(kb_name)).resolve()
    file_path = (kb_path / file_name).resolve()
    return file_path

def get_loader(ext: str, file_path: str):
    loader_str = SUPPORTED_LOADERS[ext]
    loader_module = importlib.import_module("langchain_community.document_loaders")
    DocumentLoader = getattr(loader_module, loader_str)
    loader = DocumentLoader(file_path)
    return loader

def get_loader_name(ext: str):
    return SUPPORTED_LOADERS.get(ext, "None")


def make_splitter(splitter_name,chunk_size,chunk_overlap):
    splitter_name = splitter_name or "RecursiveCharacterTextSplitter"
    try:
        splitter_module = importlib.import_module("langchain_text_splitters")
        TextSplitter = getattr(splitter_module, splitter_name)
        text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    except Exception as e:
        print(e)
        splitter_module = importlib.import_module("langchain_text_splitters")
        TextSplitter = getattr(splitter_module, "RecursiveCharacterTextSplitter")
        text_splitter = TextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    return text_splitter


    

SUPPORTED_EXTS = [
    ".pdf", ".txt", ".md"
]

SUPPORTED_LOADERS = {
    ".md": "UnstructuredMarkdownLoader",
    ".pdf" : "PyPDFLoader",
    ".txt" : "TextLoader"
}

class KnowledgeFile:
    def __init__(self, filename: str, kb_name: str):
        self.kb_name = kb_name
        self.filename = filename
        self.ext = os.path.splitext(filename)[-1].lower()
        if self.ext not in SUPPORTED_EXTS:
            raise ValueError(f"暂未支持的文件格式 {self.ext}")
        self.file_path = get_file_path(kb_name, filename)
        self.pages = None
        self.splitted_docs = None
        self.text_splitter_name = None
        self.loader_name = get_loader_name(self.ext)

    
    def file2docs_main(self,
                       chunk_size=Settings.kb_settings.CHUNK_SIZE,
                       chunk_overlap=Settings.kb_settings.OVERLAP_SIZE):
        if self.splitted_docs is None:
            pages = self.file2load_1()
            self.splitted_docs = self.load2docs_2(
                pages, chunk_size, chunk_overlap
            )
        return self.splitted_docs

    def file2load_1(self):
        """
        将文件用加载器加载出来
        """
        if self.pages is None:
            loader = get_loader(self.ext, self.file_path)
            self.pages = loader.load()
        return self.pages
    
    def load2docs_2(self,pages,chunk_size,chunk_overlap):
        """
        将加载的文件进行切块变成docs
        """
        text_splitter = make_splitter(
            splitter_name=self.text_splitter_name,
            chunk_overlap=chunk_overlap,
            chunk_size=chunk_size
        )
        docs = text_splitter.split_documents(pages)
        if not docs:
            return []
        print(f"文档分割示例：{docs[0]}")
        self.splitted_docs = docs
        return self.splitted_docs

    def get_mtime(self):
        return os.path.getmtime(self.filepath)

    def get_size(self):
        return os.path.getsize(self.filepath)
# if __name__ == "__main__":
#     kb_file = KnowledgeFile(
#         filename="1.病理生理学（第10版）.pdf",
#         kb_name="medicine"
#     )
#
#     kb_file.file2docs_main(chunk_size=1000,chunk_overlap=200)
#     i = 0
#     for chunk in kb_file.splitted_docs:
#         if i == 5:
#             break
#         print(chunk)
#         i+=1
