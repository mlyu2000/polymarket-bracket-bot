import asyncio
import httpx
from config import Config

async def test():
    Config.validate()
    token_id = '64469905005594457751898719080337446869920751709911938125552180158868954986760'
    url = f"https://clob.polymarket.com/book?token_id={token_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        print(resp.status_code)
        data = resp.json()
        print(data)

asyncio.run(test())
