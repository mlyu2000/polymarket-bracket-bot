import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api=PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count=0
    empty=0
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            empty+=1
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price']) + float(no_ask['price'])
        if total <= 1.005:
            print(total, m.question[:60], yes_ask['price'], no_ask['price'])
            count+=1
    print('total near', count, 'empty', empty)

asyncio.run(f())
