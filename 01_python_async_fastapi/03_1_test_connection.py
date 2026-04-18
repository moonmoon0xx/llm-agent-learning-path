# test_connection.py - 测试API连通性（已修复新版智谱AI）
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# 加载环境变量
load_dotenv()

# 测试智谱AI（新版SDK写法）
def test_zhipu():
    """测试智谱AI API连通性（新版SDK）"""
    try:
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            print("❌ 未找到ZHIPU_API_KEY环境变量")
            return False

        # 新版初始化方式
        client = ZhipuAI(api_key=api_key)

        print("🔍 正在测试智谱AI连接...")
        # 新版调用方式
        response = client.chat.completions.create(
            model="glm-4.5-Air",
            messages=[
                {"role": "user", "content": "请回复'API连接成功'"}
            ],
            temperature=0.7,
            max_tokens=20
        )

        # 新版返回格式
        result = response.choices[0].message.content
        print(f"✅ 智谱AI连接成功！")
        print(f"   响应: {result}")
        print(f"   请求ID: {response.id}")
        return True

    except ImportError:
        print("❌ 未安装zhipuai包，请运行: pip install zhipuai")
        return False
    except Exception as e:
        print(f"❌ 智谱AI测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 开始测试各API服务连通性")
    print("=" * 50)

    results = []

    # 测试智谱AI
    print("\n[1/3] 测试智谱AI...")
    results.append(("智谱AI", test_zhipu()))

    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)

    success_count = 0
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name}: {status}")
        if success:
            success_count += 1

    print(f"\n总计: {success_count}/{len(results)} 个服务连接成功")

    if success_count == 0:
        print("\n⚠️  所有服务连接失败，请检查：")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. 是否完成实名认证")
        print("4. 免费额度是否用完")
    else:
        print("\n🎉 恭喜！至少有一个服务连接成功，可以继续学习！")