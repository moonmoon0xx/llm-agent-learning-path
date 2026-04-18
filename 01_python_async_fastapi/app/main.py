# main.py - 主应用文件（最终稳定版）
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入路由
from app.routers import weather_chat

# 创建FastAPI应用
app = FastAPI(
    title="智能天气助手API",
    description="基于国内LLM的智能天气查询助手",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请替换为你的前端域名，如 ["https://yourapp.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(weather_chat.router)


# 根路由
@app.get("/")
async def root():
    return {
        "service": "智能天气助手",
        "version": "1.0.0",
        "description": "基于国内LLM的智能天气查询服务",
        "endpoints": {
            "weather_chat": "/api/weather/chat",
            "chat_history": "/api/weather/chat/history",
            "chat_stats": "/api/weather/chat/stats",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """✅ 健康检查端点（修复占位BUG）"""
    return {
        "status": "healthy",
        "service": "智能天气助手API",
        "timestamp": datetime.now().isoformat(),  # 修复：真实时间戳
        "message": "服务运行正常"
    }


# 启动应用
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))

    print("=" * 50)
    print("🚀 启动智能天气助手服务")
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"📚 API文档: http://localhost:{port}/docs")
    print("=" * 50)

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # 开发模式热重载 | 生产环境请改为 reload=False
    )