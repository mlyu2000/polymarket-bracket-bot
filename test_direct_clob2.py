import asyncio
import httpx

async def test():
    token_id = '9501097739257685311437206473199119076003324558143830373797339520803584309455'
    url = f"https://clob.polymarket.com/book?token_id={token_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        print(resp.status_code)
        print(resp.text[:2000])

asyncio.run(test())
