import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check_volumes():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    no_book = await api.fetch_order_book(m.clob_token_ids[1])
    yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
    no_ask = min(no_book.asks, key=lambda a: float(a['price']))
    print("yes ask:", yes_ask)
    print("no ask:", no_ask)
    print("yes size int:", int(float(yes_ask['size'])))
    print("no size int:", int(float(no_ask['size'])))

asyncio.run(check_volumes())
