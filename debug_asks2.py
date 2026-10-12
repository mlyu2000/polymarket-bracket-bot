import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Markets: {len(markets)}")
    detector = BracketDetector()
    count = 0
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        # Find best asks
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        count += 1
        if total <= 1.01:
            print(f"{total:.4f} | Yes {yes_price:.3f} No {no_price:.3f} | {m.question[:50]}")

    print(f"Checked {count} markets")

asyncio.run(test())
