# app/services/llm_service.py - LLM服务封装 (仅智谱AI | 新版SDK)
import os
import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
# 🔥 导入新版智谱AI SDK
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务封装类（仅支持智谱AI）"""

    def __init__(self):
        """初始化LLM服务（固定使用智谱AI）"""
        self.provider = "zhipu"  # 固定为智谱AI
        self.client = None
        self.model = "glm-4.5-Air"  # 推荐模型，可修改

        # 统计信息
        self.total_tokens = 0
        self.total_requests = 0

        # 初始化客户端
        self.setup_client()

    def setup_client(self):
        """🔥 新版智谱AI客户端初始化"""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("ZHIPU_API_KEY环境变量未设置")

        # 新版SDK核心代码
        self.client = ZhipuAI(api_key=api_key)
        logger.info(f"LLM服务初始化成功，使用 智谱AI 提供商")

    def chat(self,
             messages: List[Dict],
             temperature: float = 0.7,
             max_tokens: int = 500,
             tools: Optional[List] = None) -> Dict[str, Any]:  #????
        """
        发送聊天请求（新版智谱AI SDK调用）

        Args:
            messages: 消息列表，格式: [{"role": "user", "content": "..."}, ...]
            temperature: 温度参数，控制随机性
            max_tokens: 最大token数
            tools: 工具定义列表（用于函数调用）

        Returns:
            Dict包含success, message, usage等信息
        """
        self.total_requests += 1

        try:
            # 🔥 新版智谱AI API调用格式
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            # 支持工具调用（函数调用）
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"

            # 新版调用方法
            response = self.client.chat.completions.create(**params)

            # 🔥 新版响应解析（属性访问，无code判断）
            usage = response.usage
            if usage:
                self.total_tokens += usage.total_tokens

            return {
                "success": True,
                "message": {
                    "role": response.choices[0].message.role,
                    "content": response.choices[0].message.content
                },
                "usage": {
                    "total_tokens": usage.total_tokens if usage else 0,
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0
                },
                "request_id": response.id,
                "provider": self.provider
            }

        except Exception as e:
            logger.error(f"LLM API调用异常: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "provider": self.provider
            }

    def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "provider": self.provider,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "avg_tokens_per_request": self.total_tokens / self.total_requests if self.total_requests > 0 else 0
        }


# 全局LLM服务实例（单例模式）
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例（单例）"""
    global _llm_service_instance

    if _llm_service_instance is None:
        _llm_service_instance = LLMService()

    return _llm_service_instance