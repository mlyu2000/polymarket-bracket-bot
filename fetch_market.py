import httpx, asyncio

async def fetch():
    async with httpx.AsyncClient(timeout=10) as client:
        url = "https://gamma-api.polymarket.com/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
        r = await client.get(url)
        data = r.json()
        m = data[1]
        print(m['question'])
        print(m['outcomePrices'])
        print(m['clobTokenIds'])

asyncio.run(fetch())
