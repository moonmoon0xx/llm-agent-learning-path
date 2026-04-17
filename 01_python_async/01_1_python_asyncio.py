import asyncio

# ==============================================
# 第一阶段：协程基础（对应：async def + await + asyncio.run）
# 练习1：模拟API请求（用asyncio.sleep模拟网络延迟）
# ==============================================
async def fetch_api_data(api_name:str,delay:float)->str:
    """
      模拟异步 API 请求
      :param api_name: API 名称（用于打印）
      :param delay: 模拟的网络延迟（秒）
      :return: 模拟的 API 返回数据
    """
    print(f"[开始]请求{api_name},预计耗时{delay}秒...")

    # 核心：使用 await 交出控制权，模拟 IO 等待
    await asyncio.sleep(delay)

    print(f"[结束]{api_name}请求完成！")
    return f"{{'data':来自{api_name}的结果}}"

async def test_basic_coroutine():
# 测试第一阶段：单个协程运行
    print("\n=== 第一阶段：单个协程运行 ===")
    result = await fetch_api_data("openai",2)
    print(f"收到数据{result}")

# ==============================================
# 第二阶段：创建任务并发执行（对应：create_task + gather）
# 练习2：并发调用多个API（模拟并发下载多个网页）
# ==============================================
async def test_concurrent_tasks():
    print("\n=== 第二阶段：并发执行多个任务 ===")
    # 方式1：用 create_task 手动创建任务
    # 任务会立即被加入事件循环队列
    task1 = asyncio.create_task(fetch_api_data("商品接口列表",1))
    task2 = asyncio.create_task(fetch_api_data("订单接口",2))
    task3 = asyncio.create_task(fetch_api_data("评论接口",1.5))

    result1 = await task1
    result2 = await task2
    result3 = await task3
    print(f"\n所有任务完成，结果：\n{result1}\n{result2}\n{result3}")
    print("\n=== 用 gather 批量并发 ===")

    apis = [
        ("首页接口", 0.8),
        ("分类接口", 1.2),
        ("搜索接口", 0.5)
    ]
    # 一次性创建所有任务并等待全部完成
    results = await asyncio.gather(
        *[fetch_api_data(name,delay) for name,delay in apis]
    )
    print(f"\ngather 批量结果：{results}")

# ==============================================
# 第三阶段：超时处理（对应：asyncio.wait_for）
# 练习3：给异步任务设置超时时间
# ==============================================

async  def test_timeout():
    print("\n=== 第三阶段：超时处理 ===")
    # 情况1：任务超时
    print("\n1. 测试超时任务（给3秒，任务需要5秒）")
    try:
        # 核心：wait_for(协程, timeout=超时时间)
        result =  await asyncio.wait_for(
            fetch_api_data("很慢的接口",5),
            timeout=3
        )
        print(f"收到结果: {result}")
    except asyncio.TimeoutError:
        print("任务超时！已自动取消")
    # 情况2：任务在超时前完成
    print("\n2. 测试正常完成的任务（给3秒，任务需要1秒）")
    try:
        result = await asyncio.wait_for(
            fetch_api_data("很快的接口",1),
            timeout=3
        )
        print(f"收到结果: {result}")
    except asyncio.TimeoutError:
        print("任务超时！")



# ==============================================
# 主函数：依次运行三个阶段的测试
# ==============================================

async def main():
    # 注释掉不需要的部分，分步运行
    await test_basic_coroutine()  # 第一阶段
    await test_concurrent_tasks()  # 第二阶段
    await test_timeout()  # 第三阶段


if __name__ == "__main__":
    # 入口：asyncio.run() 会自动创建并运行事件循环
    asyncio.run(main())