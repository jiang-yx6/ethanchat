import os
import langchain_text_splitters
from langchain_community.document_loaders import PyMuPDFLoader

import dotenv
dotenv.load_dotenv()

#Load Documents
loader = PyMuPDFLoader("D:\\ProgramFiles\\JetBrains\\PyCharmProjects\\AgentLearn\\EthanChat\\EthanChat\\data\\pdf\\已解锁\\教材资料\\1.病理生理学（第10版）.pdf")

pages = loader.load()
print(f"Loaded {len(pages)} pages")
print(pages[100].page_content)

# os.environ["OPENAI_API_KEY"] = os.getenv("LLM_API_KEY")
# model = init_chat_model(
#     model="deepseek-chat",
#     temperature=0.7,
#     timeout=30,
#     max_tokens=1000,
# )
