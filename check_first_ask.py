import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    count_under_1 = 0
    count_under_1_005 = 0
    for m in markets:
        if len(m.clob_token_ids) != 2:
            continue
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # Use first ask as script does
        yes_price = float(yes_book.asks[0]['price'])
        no_price = float(no_book.asks[0]['price'])
        total = yes_price + no_price
        if total < 1.0:
            count_under_1 += 1
        if total <= 1.005:
            count_under_1_005 += 1
    print('under 1.0:', count_under_1)
    print('under 1.005:', count_under_1_005)

asyncio.run(f())
