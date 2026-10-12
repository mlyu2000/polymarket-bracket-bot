import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'LeBron James' in m.question:
            print(m.question)
            print(m.clob_token_ids)
            yes_book = await api.fetch_order_book(m.clob_token_ids[0])
            no_book = await api.fetch_order_book(m.clob_token_ids[1])
            print('yes asks', [(a['price'], a['size']) for a in yes_book.asks[:10]])
            print('no asks', [(a['price'], a['size']) for a in no_book.asks[:10]])
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            print('min', yes_min, no_min, yes_min+no_min)
            # find size at min
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            print('size', float(yes_ask['size']), float(no_ask['size']))
            break

asyncio.run(f())
