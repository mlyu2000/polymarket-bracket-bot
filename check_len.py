import asyncio
from config import Config
import httpx

async def t():
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{Config.GAMMA_API_BASE}/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false")
        m = r.json()[0]
        tokens = m['clobTokenIds']
        print(type(tokens))
        print(len(tokens))
        print(tokens[:5])

asyncio.run(t())
