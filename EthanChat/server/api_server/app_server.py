from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from EthanChat.server.chat.kb_chat import kb_chat
import uvicorn
import argparse

def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

# --- ✅ 修改点：将路由定义移到 app 实例化之前 ---
# 我们先定义一个函数，稍后绑定到 app 上
async def kb_chat_endpoint(q: str):
    print("starting serve")
    ret = await kb_chat(
        query=q,
        kb_name="medicine",
        topk=5,
        stream=True
    )
    return ret

# 创建 app 实例
app = create_app()

# 现在再将定义好的函数注册为路由
# 这样能确保它在任何可能被导入的模块路由之前注册
@app.get("/server")
async def server_route(q: str):
    return await kb_chat_endpoint(q)

def run_api(host, port, **kwargs):
    if kwargs.get("ssl_keyfile") and kwargs.get("ssl_certfile"):
        uvicorn.run(
            app,
            host=host,
            port=port,
            ssl_keyfile=kwargs.get("ssl_keyfile"),
            ssl_certfile=kwargs.get("ssl_certfile"),
        )
    else:
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="langchain-ChatGLM",
        description="About langchain-ChatGLM, local knowledge based ChatGLM with langchain"
        " ｜ 基于本地知识库的 ChatGLM 问答",
    )
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=7861)
    parser.add_argument("--ssl_keyfile", type=str)
    parser.add_argument("--ssl_certfile", type=str)

    args = parser.parse_args()
    args_dict = vars(args)
    run_api(
        host=args.host,
        port=args.port,
        ssl_keyfile=args.ssl_keyfile,
        ssl_certfile=args.ssl_certfile,
    )