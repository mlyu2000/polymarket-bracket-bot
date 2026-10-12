import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.MIN_PROFIT_MARGIN = 0.0001
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # check first ask vs min ask
            yes_first = float(yes_book.asks[0]['price'])
            no_first = float(no_book.asks[0]['price'])
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            print(m.question[:60])
            print(' first', yes_first, no_first, yes_first+no_first)
            print(' min ', yes_min, no_min, yes_min+no_min)
            print()
asyncio.run(f())
