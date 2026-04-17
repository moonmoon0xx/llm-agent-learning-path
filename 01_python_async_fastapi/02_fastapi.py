import asyncio

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message":"天气查询API服务已启动"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/weather/{city}")
async def get_weather(city:str) :
    # TODO:
    await asyncio.sleep(0.5)#模拟网络延迟
    return {"city":city,"temperature":"待实现"}
