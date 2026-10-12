import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs, batch_size=10)
    for i, (m, (yes_book, no_book)) in enumerate(zip(markets, books)):
        if not yes_book or not no_book:
            print(f"{i}: No books")
            continue
        if not yes_book.asks or not no_book.asks:
            print(f"{i}: No asks")
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        print(f"{i}: total={total:.3f} yes={yes_price:.3f} no={no_price:.3f} liq={m.liquidity}")
        if i >= 20:
            break

asyncio.run(test())
