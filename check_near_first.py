import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    cnt = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        # Use first ask as in scan script
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total <= 1.005:
            print(f"NEAR sum {total:.3f} {m.question[:60]}")
            cnt += 1
    print("found", cnt)

asyncio.run(check())
