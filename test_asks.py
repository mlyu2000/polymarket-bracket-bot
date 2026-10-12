import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_id = m.clob_token_ids[0]
    no_id = m.clob_token_ids[1]
    yes_book = await api.fetch_order_book(yes_id)
    no_book = await api.fetch_order_book(no_id)
    print('yes asks', yes_book.asks[:5])
    print('no asks', no_book.asks[:5])

asyncio.run(test())
