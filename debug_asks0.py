import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print(f"Markets fetched: {len(markets)}")
    count = 0
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        count += 1
        # Use asks[0] as script does
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total <= 1.005:
            print(f"{total:.4f} | Yes {yes_price:.3f} No {no_price:.3f} | {m.question[:50]}")

    print(f"Checked {count} markets")

asyncio.run(test())
