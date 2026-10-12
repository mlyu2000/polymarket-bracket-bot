import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Markets: {len(markets)}")
    for m in markets:
        print(m.id, m.question[:60], m.clob_token_ids, m.liquidity)
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        print("books:", books)
        break

asyncio.run(test())
