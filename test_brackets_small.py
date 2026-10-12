import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=50)
    print(f"Fetched {len(markets)} markets")
    count = 0
    for m in markets[:20]:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        yes_price = float(yes_ask['price'])
        no_price = float(no_ask['price'])
        total = yes_price + no_price
        if total < 1.0:
            print(f"BRACKET! {m.question[:60]} total={total:.4f} yes={yes_price:.3f} no={no_price:.3f}")
            count += 1
        else:
            # print totals for debugging
            pass
    print(f"Found {count} brackets in first 20")

asyncio.run(test())
