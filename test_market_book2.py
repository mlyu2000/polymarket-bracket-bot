import asyncio
import httpx

async def test():
    url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        m = resp.json()[0]
        print(m['clobTokenIds'])
        condition = m['conditionId']
        url2 = f"https://clob.polymarket.com/book?market={condition}"
        resp2 = await client.get(url2)
        print(resp2.status_code)
        print(resp2.text[:500])

asyncio.run(test())
