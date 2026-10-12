import asyncio
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    print(len(markets))
    for m in markets[:3]:
        print(m.clob_token_ids)
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        print(books[0])
asyncio.run(test())
