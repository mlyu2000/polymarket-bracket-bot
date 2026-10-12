import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def debug():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=100)
    print(f"Fetched {len(markets)} markets")
    count = 0
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a["price"]) for a in yes_book.asks)
            no_price = min(float(a["price"]) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.0:
                print(f"BRACKET! {total:.4f} | Yes@{yes_price:.4f} No@{no_price:.4f} | {m.question[:60]}")
                count += 1
    print(f"Total brackets found: {count}")

asyncio.run(debug())
