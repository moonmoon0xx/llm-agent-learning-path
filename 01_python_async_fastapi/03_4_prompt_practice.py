# prompt_practice.py - Prompt设计练习 (新版智谱SDK)
import os
from dotenv import load_dotenv
# 🔥 新版SDK导入
from zhipuai import ZhipuAI

load_dotenv()

# 🔥 全局初始化新版AI客户端（只初始化一次，更规范）
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))
model = "glm-4.5-Air"  # 统一使用模型


def test_different_prompts():
    """测试不同的Prompt设计"""
    print("🧪 开始测试不同的Prompt设计")
    print("=" * 60)

    # 测试1：基础Prompt
    print("\n[测试1] 基础Prompt")
    response1 = client.chat.completions.create(  # 🔥 新版调用方式
        model=model,
        messages=[
            {"role": "user", "content": "北京天气怎么样？"}
        ]
    )
    # 🔥 新版取值方式
    print(f"AI回复: {response1.choices[0].message.content[:100]}...")

    # 测试2：带系统提示的Prompt
    print("\n[测试2] 带系统提示的Prompt")
    response2 = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业的天气助手，请为用户提供准确、有用的天气信息和建议。"},
            {"role": "user", "content": "北京天气怎么样？"}
        ]
    )
    print(f"AI回复: {response2.choices[0].message.content[:100]}...")

    # 测试3：结构化输出Prompt
    print("\n[测试3] 结构化输出Prompt")
    response3 = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": "你是一个天气助手。请始终以JSON格式回复，包含以下字段：temperature, condition, advice。"},
            {"role": "user", "content": "北京天气怎么样？"}
        ]
    )
    reply3 = response3.choices[0].message.content
    print(f"AI回复: {reply3[:150]}...")

    # 测试4：少样本提示（Few-shot）
    print("\n[测试4] 少样本提示（Few-shot Learning）")
    response4 = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个天气助手。根据用户的问题提供天气信息。"},
            {"role": "user", "content": "上海今天天气如何？"},
            {"role": "assistant", "content": "上海今天多云，气温18-22°C，建议穿薄外套。"},
            {"role": "user", "content": "广州明天天气怎么样？"},
            {"role": "assistant", "content": "广州明天有小雨，气温23-27°C，建议带雨伞。"},
            {"role": "user", "content": "北京今天天气怎么样？"}
        ]
    )
    print(f"AI回复: {response4.choices[0].message.content}")

    # 测试5：思维链提示（Chain of Thought）
    print("\n[测试5] 思维链提示")
    response5 = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个天气助手。请逐步推理，然后给出最终答案。"},
            {"role": "user",
             "content": "如果北京今天温度是25°C，明天比今天高3°C，后天比明天低5°C，那么后天的温度是多少？请展示你的推理过程。"}
        ]
    )
    print(f"AI回复:\n{response5.choices[0].message.content}")

    print("\n" + "=" * 60)
    print("✅ Prompt测试完成！")


def create_weather_assistant_prompt():
    """创建天气助手的完整Prompt模板"""
    print("\n📝 创建天气助手Prompt模板")
    print("=" * 60)

    weather_assistant_prompt = """你是一个专业的天气助手，具有以下特点：

1. **角色设定**：
   - 你是气象专家，能为用户提供准确、实用的天气信息
   - 语气友好、专业，但不过于正式
   - 适当时可以加入emoji表情 😊

2. **回复结构**：
   - 先概括天气状况（晴、雨、雪等）
   - 然后提供温度范围
   - 接着给出具体建议（穿衣、出行等）
   - 最后可以补充一些气象小知识

3. **注意事项**：
   - 如果用户询问的城市你不了解，诚实地告知
   - 如果涉及未来天气，说明这是预测，可能有变化
   - 对于极端天气，给出安全提醒
   - 尽量使用中文回复

请根据以上要求回答用户的天气问题。"""

    print(weather_assistant_prompt)
    print("\n🔧 使用方法：将这个Prompt放在system message中")

    return weather_assistant_prompt


if __name__ == "__main__":
    test_different_prompts()
    prompt_template = create_weather_assistant_prompt()

    # 保存Prompt模板到文件
    with open("weather_assistant_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_template)

    print("\n💾 Prompt模板已保存到 weather_assistant_prompt.txt")