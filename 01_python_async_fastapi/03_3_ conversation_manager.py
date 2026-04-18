# conversation_manager.py - 对话管理与记忆 (新版SDK)
import os
import json
from datetime import datetime
from dotenv import load_dotenv
# 1. 导入新版 SDK (新增)
from zhipuai import ZhipuAI

load_dotenv()


class ConversationManager:
    def __init__(self, max_history=10):
        """初始化对话管理器"""
        self.max_history = max_history  # 最大对话轮数
        self.conversation = []
        self.client = None  # 新版客户端对象
        self.setup_llm()

    def setup_llm(self):
        """设置LLM客户端 (已完全重构为新版)"""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY")

        # 新版 SDK 初始化方式
        self.client = ZhipuAI(api_key=api_key)
        self.model = "glm-4.5-Air"

    def add_to_conversation(self, role, content):
        """添加消息到对话历史 (逻辑未变)"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.conversation.append(message)

        # 保持对话历史不超过最大限制
        if len(self.conversation) > self.max_history * 2:  # 乘2因为包含user和assistant
            # 保留系统提示和最近的消息
            if self.conversation[0]["role"] == "system":
                # 保留系统提示
                system_msg = self.conversation[0]
                # 保留最近的n条消息
                recent_msgs = self.conversation[-(self.max_history * 2 - 1):]
                self.conversation = [system_msg] + recent_msgs
            else:
                self.conversation = self.conversation[-(self.max_history * 2):]

    def get_conversation_summary(self):
        """生成对话摘要 (API调用部分已修改)"""
        if len(self.conversation) <= 6:  # 3轮对话以内不需要摘要
            return None

        # 提取关键信息生成摘要
        summary_prompt = f"""请总结以下对话的主要内容：

对话历史：
{json.dumps(self.conversation[:-4], ensure_ascii=False, indent=2)}

请用1-2句话总结对话的核心内容，特别是用户关心的天气地点和需求。"""

        try:
            # 2. 新版 SDK 调用方式 (修改处)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3,
                max_tokens=100
            )

            # 新版直接通过属性获取内容，不需要判断 ['code']
            return response.choices[0].message.content

        except Exception as e:
            print(f"生成摘要时出错: {e}")
            pass

        return None

    def chat(self, user_input, use_summary=False):
        """处理用户输入并获取AI回复 (API调用部分已修改)"""
        print(f"\n👤 用户: {user_input}")

        # 添加用户消息
        self.add_to_conversation("user", user_input)

        # 如果对话太长，生成摘要
        summary = None
        if use_summary and len(self.conversation) > 8:
            summary = self.get_conversation_summary()
            if summary:
                print(f"📋 对话摘要: {summary}")

        # 准备发送给API的消息 (这部分逻辑未变)
        messages_to_send = []

        if summary:
            # 如果有摘要，使用摘要而不是完整历史
            if self.conversation[0]["role"] == "system":
                messages_to_send.append(self.conversation[0])

            messages_to_send.append({
                "role": "system",
                "content": f"之前的对话摘要：{summary}\n请基于这个上下文回答用户当前的问题。"
            })

            recent_messages = self.conversation[-4:]  # 最近2轮对话
            messages_to_send.extend(recent_messages)
        else:
            # 发送完整对话历史 (过滤掉 timestamp)
            messages_to_send = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.conversation
            ]

        try:
            # 3. 新版 SDK 调用方式 (修改处)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages_to_send,
                temperature=0.7,
                max_tokens=500
            )

            # 新版获取回复的方式
            ai_reply = response.choices[0].message.content
            print(f"🤖 助手: {ai_reply}")

            # 添加AI回复到对话历史
            self.add_to_conversation("assistant", ai_reply)

            return ai_reply

        except Exception as e:
            print(f"❌ 调用异常: {str(e)}")
            return None

    def start_weather_conversation(self):
        """启动天气对话 (未修改)"""
        print("=" * 60)
        print("🌤️  智能天气对话助手")
        print("=" * 60)
        print("指令:")
        print("  'history' - 查看对话历史")
        print("  'summary' - 生成对话摘要")
        print("  'clear' - 清空对话历史")
        print("  'quit' - 退出")
        print("=" * 60)

        # 初始化系统提示
        system_prompt = """你是一个专业的天气助手。请遵循以下规则：
1. 专注于回答天气相关问题
2. 如果用户询问非天气问题，礼貌地引导回天气话题
3. 提供实用的穿衣、出行建议
4. 记住用户之前提到的地点偏好"""

        self.add_to_conversation("system", system_prompt)

        print("💡 提示：你可以问不同城市的天气，或者进行多轮对话")

        while True:
            try:
                user_input = input("\n💭 你的问题: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break

                elif user_input.lower() == 'history':
                    self.show_conversation_history()
                    continue

                elif user_input.lower() == 'summary':
                    summary = self.get_conversation_summary()
                    if summary:
                        print(f"\n📋 当前对话摘要: {summary}")
                    else:
                        print("\n📋 对话太短，无需摘要")
                    continue

                elif user_input.lower() == 'clear':
                    self.conversation = []
                    self.add_to_conversation("system", system_prompt)
                    print("🗑️  对话历史已清空")
                    continue

                elif not user_input:
                    print("⚠️  请输入内容")
                    continue

                # 处理对话
                self.chat(user_input, use_summary=True)

            except KeyboardInterrupt:
                print("\n\n👋 用户中断，再见！")
                break

    def show_conversation_history(self):
        """显示对话历史 (未修改)"""
        print("\n" + "=" * 60)
        print("📜 完整对话历史")
        print("=" * 60)

        for i, msg in enumerate(self.conversation):
            role_display = {
                "system": "📋 系统",
                "user": "👤 用户",
                "assistant": "🤖 助手"
            }.get(msg["role"], msg["role"])

            # 显示时间
            time_str = ""
            if "timestamp" in msg:
                try:
                    dt = datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    pass

            content = msg["content"]
            if len(content) > 80:
                content = content[:77] + "..."

            print(f"{i + 1:2d}. [{time_str}] {role_display}: {content}")

        print(f"\n总计: {len(self.conversation)} 条消息")


# 主函数
def main():
    print("启动对话管理器...")

    try:
        manager = ConversationManager(max_history=5)  # 最多记住5轮对话
        manager.start_weather_conversation()
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")


if __name__ == "__main__":
    main()