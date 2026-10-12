import asyncio
import httpx

async def test():
    condition_id = '0x7b0f323f4082e1830bf728139ae4b8206fdd9ab979086f7785d8a4f6543f7d70'
    url = f"https://clob.polymarket.com/book?market={condition_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        print(resp.status_code)
        print(resp.json())

asyncio.run(test())
