import asyncio
import httpx

async def test():
    # fetch markets
    url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        m = resp.json()[0]
        print("clobTokenIds:", m['clobTokenIds'])
        print("conditionId:", m['conditionId'])
        # try book with market param?
        token_id = m['clobTokenIds'][0]
        # Maybe need to use market endpoint: /book?market=... ? Let's search.
        # Try /book?token_id with hex? maybe token id is decimal string, need to convert?
        # Let's try fetching order book for market via gamma?
        # Try data-api
        url2 = f"https://data-api.polymarket.com/markets?ids={m['id']}"
        resp2 = await client.get(url2)
        print(resp2.status_code)
        print(resp2.json())

asyncio.run(test())
