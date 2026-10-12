import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1000)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    found = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
        no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
        total = yes_price + no_price
        if total < 1.0:
            found += 1
            print(f"{total:.4f} {m.question[:70]} liq {m.liquidity}")
    print("found", found)

asyncio.run(t())
