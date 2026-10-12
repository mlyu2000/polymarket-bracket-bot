import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    totals = []
    for m in markets:
        if len(m.clob_token_ids) != 2:
            continue
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_best = min(yes_book.asks, key=lambda a: float(a['price']))
        no_best = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_best['price']) + float(no_best['price'])
        totals.append(total)
    if totals:
        print('min total', min(totals))
        print('max total', max(totals))
        print('avg total', sum(totals)/len(totals))
        under_1 = [t for t in totals if t < 1.0]
        under_1_005 = [t for t in totals if t <= 1.005]
        print('under 1.0 count', len(under_1))
        print('under 1.005 count', len(under_1_005))

asyncio.run(f())
