import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    # Find Timothée market
    for m in markets:
        if 'Timothée Chalamet' in m.question:
            print(f"Found: {m.question}")
            print(f"Liquidity: {m.liquidity}")
            token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
            books = await api.fetch_order_books_batch(token_pairs)
            yes_book, no_book = books[0]
            print(f"Yes asks[0]: {yes_book.asks[0] if yes_book.asks else None}")
            print(f"No asks[0]: {no_book.asks[0] if no_book.asks else None}")
            print(f"Yes min ask: {min(yes_book.asks, key=lambda a: float(a['price']))}")
            print(f"No min ask: {min(no_book.asks, key=lambda a: float(a['price']))}")
            break

asyncio.run(test())
