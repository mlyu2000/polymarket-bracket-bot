import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_id = m.clob_token_ids[0]
    book = await api.fetch_order_book(yes_id)
    print("asks:", book.asks[:10])
    prices = [float(a['price']) for a in book.asks]
    print("prices:", prices)
    print("min:", min(prices), "first:", prices[0])
    # check if sorted
    print("is ascending?", all(prices[i] <= prices[i+1] for i in range(len(prices)-1)))

asyncio.run(test())
