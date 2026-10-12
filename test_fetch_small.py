import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Fetched {len(markets)} markets")
    for m in markets:
        print(m.question[:80], m.liquidity, m.clob_token_ids)
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in [m]]
        books = await api.fetch_order_books_batch(token_pairs)
        print("books:", books)

asyncio.run(test())
