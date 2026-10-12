import asyncio
import httpx

async def test():
    url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        m = resp.json()[0]
        print(m['clobTokenIds'])
        # try the other token
        token_id = m['clobTokenIds'][1]
        print("token2 hex:", hex(int(token_id)))
        # search for book endpoint documentation maybe uses conditionId
        # Let's try GET /book?market=0x...
        condition = m['conditionId']
        url2 = f"https://clob.polymarket.com/book?market={condition}"
        resp2 = await client.get(url2)
        print(resp2.status_code, resp2.text[:200])

asyncio.run(test())
