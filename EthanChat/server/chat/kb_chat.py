from typing import Literal, List, Tuple, Union, Dict,Optional
from pydantic import BaseModel
import asyncio
import uuid
import time
import json
from EthanChat.settings import Settings
from EthanChat.server.utils import (
    BaseResponse,
    check_embed_model,
    get_ChatOpenAI_llm,
    get_default_llm,
    get_prompt_template
)
from EthanChat.server.knowledge_base.base import KBServiceFactory
from fastapi import Body
from sse_starlette.sse import EventSourceResponse
from langchain_classic.callbacks import AsyncIteratorCallbackHandler
from langchain_core.prompts import ChatMessagePromptTemplate, ChatPromptTemplate

class History(BaseModel):
    role: str
    content: str

    def to_msg_template(self) -> ChatMessagePromptTemplate:
        role_map = {
            "ai": "assistant",
            "human": "user",
        }
        role = role_map.get(self.role, self.role)
        content = self.content

        return ChatMessagePromptTemplate.from_template(
            content,
            "jinja2",
            role=role,
        )


    @classmethod
    def from_data(cls, h: Union[List, Tuple, Dict]) -> "History":
        if isinstance(h, (list, tuple)) and len(h) >= 2:
            h = cls(role=h[0], content=h[1])
        elif isinstance(h,dict):
            h = cls(**h)
        return h
    
async def kb_chat(
        query: str,
        kb_name: str,
        topk: int,
        score_threshold: float = Settings.kb_settings.SCORE_THRESHOLD,
        history: list[History] = [],
        stream: bool = True,
        model: str = get_default_llm(),
        temperature: float = Settings.model_settings.TEMPERATURE,
        max_tokens: Optional[int] = Settings.model_settings.MAX_TOKENS,
        prompt_name: str = "default",
):
    service = KBServiceFactory.get_service(kb_name=kb_name ,vs_type="chroma")
    if service is None:
        return BaseResponse(code=404, msg=f"未找到本地对应知识库 {kb_name}")
    

    async def knowledge_base_chat_iterator():
        try:
            nonlocal history, prompt_name, max_tokens
            history = [History.from_data(h) for h in history]
            ok, msg = check_embed_model(service.embed_model)
            if not ok:
                raise ValueError(msg)
            print(f"local knowledge base: {service.kb_name}")
            print(f"查询参数: query={query}, topk={topk}, score_threshold={score_threshold}")

            # 直接测试 ChromaDB
            # print("\n=== 直接测试 ChromaDB ===")
            # try:
            #     test_results = service.chroma.similarity_search_with_score(query, k=topk)
            #     print(f"ChromaDB 原始返回: {len(test_results)} 个结果")
            #     for i, (doc, score) in enumerate(test_results[:3]):
            #         print(f"  结果 {i+1}: score={score:.4f}, 内容前50字: {doc.page_content[:50]}")
            # except Exception as e:
            #     print(f"ChromaDB 测试失败: {e}")

            docs = service.search_docs(
                        query=query,
                        top_k=topk,
                        score_threshold=1.5,
                    )
            print(f"\nservice.search_docs 返回: {len(docs)} 个文档")
            print(f"文档详情: {docs}")
            import os
            docs_info = [
                f"""出处 [{i + 1}] [{d[0].metadata.get('source', '未知文件')}] {d[0].page_content}"""
                for i, d in enumerate(docs)
            ]
            print("docs_info:",docs_info )

            context = "\n\n".join([doc[0].page_content for doc in docs])

            if len(docs) == 0:
                prompt_name = "empty"

            prompt_template = get_prompt_template("rag", prompt_name)

            input_msg = History(role="user", content=prompt_template).to_msg_template()
            chat_prompt = ChatPromptTemplate.from_messages(
                [i.to_msg_template() for i in history]  + [input_msg]
            )

            if stream:
                # 流式输出
                callback = AsyncIteratorCallbackHandler()

                llm = get_ChatOpenAI_llm(
                    model_name=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    streaming=True,
                    callbacks=[callback]
                )

                chain = chat_prompt | llm
                task = asyncio.create_task(chain.ainvoke({"context": context, "question": query}))

                # 先发送初始消息
                ret = {
                    "id": f"chat{uuid.uuid4()}",
                    "object": "chat.completion.chunk",
                    "model": model,
                    "created": time.time(),
                    "status": "Agentic RAG",
                }
                yield json.dumps(ret) + "\n"

                # 流式输出 token
                async for token in callback.aiter():
                    ret = {
                        "id": f"chat{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "model": model,
                        "created": time.time(),
                        "choices": [{
                            "delta": {"content": token},
                            "index": 0
                        }]
                    }
                    print(token,end="")
                    yield json.dumps(ret) + "\n"

                await task
            else:
                # 非流式输出
                llm = get_ChatOpenAI_llm(
                    model_name=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    streaming=False
                )
                chain = chat_prompt | llm
                result = await chain.ainvoke({"context": context, "question": query})
                ret = {
                    "id": f"chat{uuid.uuid4()}",
                    "object": "chat.completion",
                    "model": model,
                    "created": time.time(),
                    "choices": [{
                        "message": {"role": "assistant", "content": result.content},
                        "index": 0,
                        "finish_reason": "stop"
                    }]
                }

                yield json.dumps(ret) + "\n"
        except Exception as e:
            yield {"data": json.dumps({"error": str(e)})}
            return
    return EventSourceResponse(knowledge_base_chat_iterator())


# import asyncio
import pytest
#
# @pytest.mark.asyncio
# async def test_kb_chat():
#     # 调用你的异步函数
#     # 注意：kb_chat 返回的是 EventSourceResponse，你需要测试其内部逻辑或返回值
#     response = await kb_chat(
#         query="在病理生理学中，“病因学”（Etiology）和“发病机制”（Pathogenesis）分别指的是什么",
#         kb_name="medicine",
#         topk=5,
#         stream=True
#     )
#
#     # 这里需要根据你的返回类型进行断言
#     # 例如检查返回的是否是 EventSourceResponse 实例
#     from sse_starlette.sse import EventSourceResponse
#     assert isinstance(response, EventSourceResponse)
#
#     async for chunk in response.body_iterator:
#         # chunk 通常是字符串格式的 JSON
#         print("-" * 30)
#         print(f"原始输出: {chunk}")
#
#         # 如果想看格式化后的内容，可以解析一下
#         try:
#             data = json.loads(chunk)
#             print(f"完整数据: {data}")
#         except:
#             print(f"无法解析JSON: {chunk}")