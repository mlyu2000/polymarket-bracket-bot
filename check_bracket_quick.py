from polymarket_api import PolymarketAPI
from detector import BracketDetector
from config import Config
import asyncio

async def f():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=200)
    found = 0
    for m in markets[:50]:
        yes_id, no_id = m.clob_token_ids[0], m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(yes_book.asks[-1]['price'])
        no_price = float(no_book.asks[-1]['price'])
        total = yes_price + no_price
        if total < 1.0:
            print('BRACKET', m.question[:60], total, yes_price, no_price)
            found += 1
    print('found', found)

asyncio.run(f())
