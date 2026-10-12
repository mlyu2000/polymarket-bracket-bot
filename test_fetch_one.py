import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Fetched {len(markets)} markets")
    for m in markets[:3]:
        print(m.question[:80], m.liquidity, m.clob_token_ids)
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        print("yes_book:", yes_book.asks[:2] if yes_book else None)
        print("no_book:", no_book.asks[:2] if no_book else None)

asyncio.run(test())
