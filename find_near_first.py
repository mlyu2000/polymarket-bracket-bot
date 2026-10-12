import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    count = 0
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total < 1.005:
            print('found', total, yes_price, no_price, m.question[:60])
            count += 1
    print('total found', count)

asyncio.run(f())
