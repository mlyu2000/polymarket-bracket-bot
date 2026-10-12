import asyncio, httpx
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    # search for market
    url = "https://gamma-api.polymarket.com/markets?limit=1000&active=true&closed=false&order=volume&ascending=false"
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(url)
        markets = resp.json()
    target = None
    for m in markets:
        if 'Sao Paulo' in m.get('question',''):
            target = m
            break
    print(target)
    if not target:
        return
    yes_id = target['clobTokenIds'][0]
    no_id = target['clobTokenIds'][1]
    print('ids', yes_id, no_id)
    # fetch books
    from polymarket_api import PolymarketAPI
    api = PolymarketAPI()
    yes_book = await api.fetch_order_book(yes_id)
    no_book = await api.fetch_order_book(no_id)
    print('yes asks', yes_book.asks[:5])
    print('no asks', no_book.asks[:5])
    # compute min
    yes_min = min(float(a['price']) for a in yes_book.asks)
    no_min = min(float(a['price']) for a in no_book.asks)
    print('min', yes_min, no_min, yes_min+no_min)

asyncio.run(test())
