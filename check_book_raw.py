import asyncio
from polymarket_api import PolymarketAPI
from config import Config

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_id = m.clob_token_ids[0]
    book = await api.fetch_order_book(yes_id)
    print("market:", m.question[:60])
    print("asks:", book.asks[:10])
    print("bids:", book.bids[:10])

asyncio.run(test())
