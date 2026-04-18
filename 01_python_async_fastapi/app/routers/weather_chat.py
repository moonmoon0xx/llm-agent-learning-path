# app/routers/weather_chat.py - 天气聊天路由 (修复优化版)
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
# 修复1：移除无用导入 import json
# 修复2：异步调用同步函数的解决方案
from asgiref.sync import sync_to_async

from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/api/weather", tags=["weather_chat"])


# ===================== 数据模型（增加校验）=====================
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息", min_length=1)
    city: Optional[str] = None
    use_history: Optional[bool] = True
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="随机性参数0-1")
    max_tokens: Optional[int] = Field(500, ge=100, le=2000, description="最大回复长度")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool
    message: str
    city: Optional[str] = None
    ai_reply: Optional[str] = None
    tokens_used: Optional[int] = 0
    response_time: Optional[float] = 0.0
    timestamp: str


# ===================== 全局配置 =====================
# 对话历史存储（演示用内存存储，生产环境请使用 Redis）
conversation_histories = {}

# 天气助手系统提示（无修改）
WEATHER_ASSISTANT_PROMPT = """你是一个专业的天气助手。请遵循以下规则：

1. **角色设定**：
   - 你是气象专家，提供准确、实用的天气信息
   - 语气友好、专业，使用中文回复
   - 可以适当使用emoji表情 😊☀️🌧️

2. **回复结构**：
   - 先回答用户的具体问题
   - 提供温度、天气状况、风力等关键信息
   - 给出实用的建议（穿衣、出行等）
   - 可以补充相关气象知识

3. **注意事项**：
   - 如果不知道真实天气数据，可以基于常识或典型气候回答
   - 对于极端天气，给出安全提醒
   - 如果用户问题不明确，可以询问具体城市或时间
"""


# ===================== 核心接口 =====================
@router.post("/chat", response_model=ChatResponse)
async def chat_about_weather(request: ChatRequest, client_req: Request):
    """
    与天气助手聊天
    支持多轮对话，自动管理对话历史
    """
    import time
    start_time = time.time()

    # 修复3：使用客户端IP作为用户ID，避免所有用户串聊
    user_id = client_req.client.host

    # 修复4：异步包装同步的LLM调用（解决FastAPI阻塞）
    @sync_to_async
    def call_llm(messages):
        llm_service = get_llm_service()
        return llm_service.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

    # 准备消息列表
    messages = []

    # 获取或初始化对话历史
    if request.use_history and user_id in conversation_histories:
        messages = conversation_histories[user_id]

        # 优化1：更简洁的历史长度限制（最多10轮=20条消息）
        if len(messages) > 20:
            messages = messages[-20:]
    else:
        # 初始化新对话
        messages = [{"role": "system", "content": WEATHER_ASSISTANT_PROMPT}]

    # 优化2：空消息校验（已通过Pydantic min_length保证，此处冗余可删）
    user_message = request.message.strip()

    # 拼接城市信息
    if request.city:
        user_message = f"关于{request.city}的天气：{user_message}"

    # 添加用户消息
    messages.append({"role": "user", "content": user_message})

    # 异步调用AI服务
    response = await call_llm(messages)

    response_time = time.time() - start_time

    if response["success"]:
        ai_reply = response["message"]["content"]
        messages.append({"role": "assistant", "content": ai_reply})
        conversation_histories[user_id] = messages

        tokens_used = response.get("usage", {}).get("total_tokens", 0)

        return ChatResponse(
            success=True,
            message="聊天成功",
            city=request.city,
            ai_reply=ai_reply,
            tokens_used=tokens_used,
            response_time=round(response_time, 3),
            timestamp=datetime.now().isoformat()
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"AI服务调用失败: {response.get('error', '未知错误')}"
        )


# ===================== 辅助接口（无修改，仅规范）=====================
@router.get("/chat/history")
async def get_chat_history(request: Request):
    """获取当前用户对话历史"""
    user_id = request.client.host
    history = []
    if user_id in conversation_histories:
        history = [msg for msg in conversation_histories[user_id] if msg["role"] in ["user", "assistant"]]

    return {
        "success": True,
        "user_id": user_id,
        "history": history,
        "total_messages": len(history)
    }


@router.delete("/chat/history")
async def clear_chat_history(request: Request):
    """清空当前用户对话历史"""
    user_id = request.client.host
    if user_id in conversation_histories:
        del conversation_histories[user_id]

    return {
        "success": True,
        "message": f"用户 {user_id} 的对话历史已清空"
    }


@router.get("/chat/stats")
async def get_chat_stats():
    """获取聊天统计信息"""

    @sync_to_async
    def get_stats():
        return get_llm_service().get_stats()

    stats = await get_stats()
    return {
        "success": True,
        "stats": stats,
        "active_conversations": len(conversation_histories),
        "timestamp": datetime.now().isoformat()
    }