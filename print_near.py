import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets[:100]:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total <= 1.01:
            print(total, yes_price, no_price, m.question[:60])

asyncio.run(f())
