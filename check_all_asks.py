import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'LeBron James' in m.question:
            yes_book = await api.fetch_order_book(m.clob_token_ids[0])
            no_book = await api.fetch_order_book(m.clob_token_ids[1])
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            print('yes price', yes_ask['price'], 'size', yes_ask['size'])
            print('no price', no_ask['price'], 'size', no_ask['size'])
            # check if ask price is best?
            # print all asks
            print('all yes asks prices')
            for a in yes_book.asks:
                print(a['price'])
            break

asyncio.run(f())
