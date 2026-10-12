import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=1)
    print(m[0].clob_token_ids)
    b = await api.fetch_order_books_batch([(m[0].clob_token_ids[0], m[0].clob_token_ids[1])])
    y,n = b[0]
    print('yes asks', y.asks[:3] if y else None)
    print('no asks', n.asks[:3] if n else None)

asyncio.run(t())
