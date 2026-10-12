import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    print("asks count", len(yes_book.asks))
    print(yes_book.asks[:10])

asyncio.run(test())
