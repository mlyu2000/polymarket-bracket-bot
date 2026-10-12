import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    api=PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    count=0
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book:
            continue
        # find min ask
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price']) + float(no_ask['price'])
        if total <= 1.005:
            print(total, m.question[:60], yes_ask['price'], no_ask['price'])
            count+=1
    print('total', count)

asyncio.run(f())
