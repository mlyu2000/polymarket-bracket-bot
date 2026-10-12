import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print(f"Market: {m.question[:60]}")
        print(f"  liquidity: {m.liquidity}, active: {m.active}, closed: {m.closed}")
        print(f"  clob_token_ids: {m.clob_token_ids}")
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        print(f"  yes_book exists: {yes_book is not None}, asks: {len(yes_book.asks) if yes_book else 0}")
        print(f"  no_book exists: {no_book is not None}, asks: {len(no_book.asks) if no_book else 0}")
        if yes_book and yes_book.asks:
            print(f"  yes asks: {yes_book.asks[:3]}")
        if no_book and no_book.asks:
            print(f"  no asks: {no_book.asks[:3]}")
        print()

asyncio.run(test())
