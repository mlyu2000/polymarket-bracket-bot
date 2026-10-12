import asyncio
from polymarket_api import PolymarketAPI

async def scan():
    api = PolymarketAPI()
    # fetch with liquidity ascending
    from config import Config
    # monkey patch sort
    orig_sort = Config.SCAN_SORT_BY
    # We'll directly call API with different params
    import httpx
    gamma_base = Config.GAMMA_API_BASE
    url = f"{gamma_base}/markets?limit=100&offset=0&active=true&closed=false&order=liquidity&ascending=true"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        data = resp.json()
    print(f"got {len(data)} markets")
    for m in data[:10]:
        print(m.get('question')[:60], m.get('liquidity'))

asyncio.run(scan())
