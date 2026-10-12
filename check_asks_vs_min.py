import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m,(yes_book,no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total <= 1.005:
            print(f"{total:.4f} asks0 {m.question[:60]}")
            # also check min
            yes_min = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
            no_min = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
            print(f"{yes_min+no_min:.4f} min {m.question[:60]}")

asyncio.run(t())
