# -*- coding: utf-8 -*-
"""
@Project : copilot_demo
@File    : main.py
@Date    : 2025/12/17 20:58
@Desc    :
"""

import asyncio
import threading

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from typing import List
import os
import uuid

from src.copilot.agent import get_session, delete_session
from src.copilot.config.config import STATIC_DIR
from src.copilot.schemas.api_schemas import ChatRequest, CleanRequest
from src.copilot.utils.logger import logger


# 上传文件存储目录
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 初始化FastAPI应用
app = FastAPI(title="AI对话助手", version="1.0")

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# 多文件上传接口（修改）
@app.post("/api/upload", summary="上传附件（支持多个）")
async def upload_files(files: List[UploadFile] = File(...)):  # 改为接收文件列表
    upload_results = []

    for file in files:
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        file_name = f"{uuid.uuid4()}.{file_ext}" if file_ext else f"{uuid.uuid4()}"
        file_save_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_save_path, "wb") as f:
            f.write(await file.read())

        upload_results.append({
            "original_name": file.filename,
            "file_path": file_save_path,
        })

    return JSONResponse(content=upload_results)  # 返回文件信息列表


# AI对话接口（修改为支持多附件）
@app.post("/api/chat", summary="AI对话（流式输出）")
async def chat(chat_request: ChatRequest):
    """接收前端的对话内容和附件信息，流式返回AI回复（支持Markdown）"""
    attachments = chat_request.attachments or []  # 处理多附件
    agent = get_session(chat_request.session_id)
    attachments_content = ''
    if attachments:
        attachments_content = agent.parse_attachments(attachments)
    user_content = f'{attachments_content}\n {chat_request.content}'
    thread_chat = threading.Thread(target=agent.chat,args=(user_content,))
    thread_chat.daemon = True
    thread_chat.start()

    # 模拟AI思考和生成过程
    async def generate_response():
        while True:
            try:
                data = agent.que.get(timeout=200)
            except Exception as e:
                logger.error("获取队列数据异常：%s" % str(e))
                break
            if data is None or data == "~end":
                yield "~end~"
                break
            print(data, end="", flush=True)
            await asyncio.sleep(0.1)
            yield data

    # 返回流式响应
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream"
    )


# 文件删除接口（不变）
@app.post("/api/delete-file", summary="删除已上传的文件")
async def delete_file(request: Request):
    data = await request.json()
    file_full_path = data.get("file_full_path", "")

    if not file_full_path.startswith(UPLOAD_DIR):
        return JSONResponse(content={"success": False, "msg": "文件路径不合法"}, status_code=400)

    try:
        if os.path.exists(file_full_path):
            os.remove(file_full_path)
            return JSONResponse(content={"success": True, "msg": "文件删除成功"})
        else:
            return JSONResponse(content={"success": False, "msg": "文件不存在"})
    except Exception as e:
        return JSONResponse(content={"success": False, "msg": f"文件删除失败：{str(e)}"}, status_code=500)


@app.post("/api/clean", summary="清理会话数据")
async def clean(clean_request: CleanRequest):
    agent = get_session(clean_request.session_id)
    for attachment in agent.attachments:
        if attachment.file_path:
            os.remove(attachment.file_path)
    delete_session(clean_request.session_id)


# 根路由（不变）
@app.get("/", summary="前端对话页面")
async def get_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
