# first_chat.py - 智谱AI专属聊天程序
import os
from dotenv import load_dotenv
from datetime import datetime
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()


class SimpleChat:
    def __init__(self):
        """初始化智谱AI聊天程序"""
        self.conversation_history = []
        self.setup_client()

    def setup_client(self):
        """设置智谱AI客户端"""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 文件中设置 ZHIPU_API_KEY")
        self.client = ZhipuAI(api_key=api_key)
        self.model = "glm-4.5-Air"  # 可切换为 "glm-3-turbo" 更快速

    def add_message(self, role, content):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def chat(self, user_input):
        """发送消息并获取回复"""
        print(f"\n👤 你: {user_input}")

        # 添加用户消息到历史
        self.add_message("user", user_input)

        try:
            # 过滤掉timestamp和system消息，只保留role和content
            messages_for_api = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.conversation_history if msg["role"] != "system"
            ]

            # 调用智谱AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages_for_api,
                temperature=0.7,
                max_tokens=500
            )

            ai_reply = response.choices[0].message.content
            print(f"🤖 AI: {ai_reply}")
            self.add_message("assistant", ai_reply)
            return ai_reply

        except Exception as e:
            print(f"❌ API调用异常: {str(e)}")
            return None

    def start_interactive(self):
        """启动交互式聊天"""
        print("=" * 50)
        print("🚀 智谱AI (GLM-4) 聊天程序已启动")
        print("输入 'quit' 或 '退出' 结束对话")
        print("输入 'history' 查看对话历史")
        print("输入 'clear' 清空对话历史")
        print("=" * 50)

        # 设置系统提示
        system_prompt = "你是一个有帮助的AI助手。请用中文回答用户的问题。"
        self.add_message("system", system_prompt)

        while True:
            try:
                user_input = input("\n💭 请输入: ").strip()

                if user_input.lower() in ['quit', '退出', 'exit']:
                    print("👋 再见！")
                    break

                elif user_input.lower() == 'history':
                    self.show_history()
                    continue

                elif user_input.lower() == 'clear':
                    self.conversation_history = [
                        {"role": "system", "content": "你是一个有帮助的AI助手。请用中文回答用户的问题。"}
                    ]
                    print("🗑️  对话历史已清空")
                    continue

                elif not user_input:
                    print("⚠️  输入不能为空")
                    continue

                # 调用聊天
                self.chat(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 用户中断，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")

    def show_history(self):
        """显示对话历史"""
        print("\n" + "=" * 50)
        print("📜 对话历史")
        print("=" * 50)

        for i, msg in enumerate(self.conversation_history):
            role_map = {
                "system": "📋 系统",
                "user": "👤 用户",
                "assistant": "🤖 AI"
            }
            role_display = role_map.get(msg["role"], msg["role"])

            # 截断长消息以便显示
            content = msg["content"]
            if len(content) > 100:
                content = content[:97] + "..."

            print(f"{i + 1}. {role_display}: {content}")

        print(f"\n总计 {len(self.conversation_history)} 条消息")


# 主函数
def main():
    try:
        chat = SimpleChat()
        chat.start_interactive()
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        print("请检查:")
        print("1. 是否安装了依赖: pip install zhipuai python-dotenv")
        print("2. 是否在 .env 文件中正确设置了 ZHIPU_API_KEY")


if __name__ == "__main__":
    main()