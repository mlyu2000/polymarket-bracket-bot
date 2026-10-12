import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count = 0
    near = 0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # using asks[0] as in script
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        count += 1
        if total <= 1.005:
            print(f"Near: {total:.4f} yes={yes_price} no={no_price} {m.question[:60]}")
            near += 1
    print(f"Checked {count} markets, near misses {near}")

asyncio.run(check())
