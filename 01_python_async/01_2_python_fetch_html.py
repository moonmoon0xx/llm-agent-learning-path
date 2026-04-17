import asyncio
import aiohttp

async def fetch_real_page(url:str)->str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return f"✅ {url} 下载完成，长度：{len(content)} 字符"

async def concurrent_get_page():
    print("\n=== 并发获取网页 === ")
    urls = [
        "https://httpbin.org/get",
        "https://example.com",
        "https://www.baidu.com"
    ]
    results = await asyncio.gather(
        *[fetch_real_page(url) for url in urls]
    )
    print(f"\n gather 批量结果:{results}")

async def main():
   await concurrent_get_page()

if __name__ == "__main__":
    asyncio.run(main())