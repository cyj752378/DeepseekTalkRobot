# -*- coding: utf-8 -*-
"""
@Project : DeepseekTalkRobot
@File    : main.py.py
@Author  : huJunChai
@Desc    : 文件功能描述
"""
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Depends  # FastAPI 核心组件
from fastapi.middleware.cors import CORSMiddleware  # 处理跨域
from pydantic import BaseModel  # 定义请求/响应的数据结构（数据验证）
from langchain_deepseek import ChatDeepSeek # LangChain 集成的 DeepSeek 客户端
from dotenv import load_dotenv  # 加载 .env 文件
import os  # 操作系统相关（读取环境变量）

# 加载环境变量（读取 .env 文件里的 API Key）
load_dotenv()

# 初始化 FastAPI 应用（创建一个 API 服务实例）
app = FastAPI(title="DeepSeek Chat API")

# 配置 CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有前端域名访问（生产环境要指定具体域名，更安全）
    allow_credentials=True,  # 允许携带 Cookie
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET/POST 等）
    allow_headers=["*"],  # 允许所有请求头
)

# 配置静态文件服务（让后端能访问 static 目录下的前端文件）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 定义请求体结构（前端给后端发消息时，必须按照这个格式传数据）
class ChatRequest(BaseModel):
    message: str  # 必传字段：用户的提问消息
    system_prompt: str = "你是一个有用的助手..."  # 可选字段：系统提示词（默认值）
    temperature: float = 0.7  # 可选字段：控制回复随机性（0=严谨，1=随机）

# 定义响应体结构（后端给前端返回数据时，按照这个格式返回）
class ChatResponse(BaseModel):
    response: str  # 必传字段：助手的回复内容
    status: str = "success"  # 可选字段：状态（默认成功）

# 验证并获取 DeepSeek API Key（依赖注入函数）
def get_deepseek_api_key():
    api_key = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量读取 API Key
    if not api_key:  # 如果没配置 API Key，抛出 500 错误
        raise HTTPException(status_code=500, detail="DeepSeek API Key 未配置")
    return api_key

# 初始化 DeepSeek 聊天模型（依赖注入函数）
def get_chat_model(api_key: str = Depends(get_deepseek_api_key)):
    try:
        return ChatDeepSeek(
            api_key=api_key,  # 传入 API Key
            model_name="deepseek-chat",  # 指定使用的 DeepSeek 模型（基础聊天模型）
            temperature=0.7,  # 默认温度（可被前端请求覆盖）
            max_tokens=2048  # 最大回复长度（2048 个字符）
        )
    except Exception as e:  # 初始化失败（比如 API Key 无效），抛出 500 错误
        raise HTTPException(status_code=500, detail=f"初始化模型失败: {str(e)}")

# 根路径跳转前端页面
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.post("/api/chat", response_model=ChatResponse)  # POST 方法，接口路径 /api/chat，响应格式遵循 ChatResponse
async def chat(
        request: ChatRequest,  # 接收前端传来的请求数据（自动验证格式）
        chat_model: ChatDeepSeek = Depends(get_chat_model)  # 自动获取初始化好的 DeepSeek 模型
):
    try:
        # 1. 构建消息列表（LangChain 要求的格式：系统提示 + 用户消息）
        messages = [
            {"role": "system", "content": request.system_prompt},  # 系统设置
            {"role": "user", "content": request.message}  # 你的问题
        ]

        # 2. 调用 DeepSeek API（通过 LangChain 的模型实例）
        response = chat_model.invoke(messages)  # invoke() 是 LangChain 调用模型的统一方法

        # 3. 返回响应（遵循 ChatResponse 格式）
        return ChatResponse(response=response.content)

    except Exception as e:  # 捕获所有异常（比如 API 调用失败），返回 500 错误
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)