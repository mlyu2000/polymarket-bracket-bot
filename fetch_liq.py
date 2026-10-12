import httpx, asyncio

async def fetch_markets():
    async with httpx.AsyncClient(timeout=10) as client:
        url = "https://gamma-api.polymarket.com/markets?limit=100&offset=0&active=true&closed=false&order=liquidity&ascending=true"
        r = await client.get(url)
        data = r.json()
        print(f"Fetched {len(data)} markets")
        for m in data[:10]:
            print(m['question'][:60], m.get('liquidity'), m.get('clobTokenIds'))

asyncio.run(fetch_markets())
