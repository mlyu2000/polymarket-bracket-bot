import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    min_total = 2
    best = None
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(yes_book.asks[-1]['price'])
        no_price = float(no_book.asks[-1]['price'])
        total = yes_price + no_price
        if total < min_total:
            min_total = total
            best = (total, yes_price, no_price, m.question)
    print(min_total, best)

asyncio.run(f())
