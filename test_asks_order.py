import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test_asks():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    m = markets[0]
    print(m.question)
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    no_book = await api.fetch_order_book(m.clob_token_ids[1])
    print("yes asks sample:", yes_book.asks[:10])
    # find min
    yes_prices = [float(a['price']) for a in yes_book.asks]
    no_prices = [float(a['price']) for a in no_book.asks]
    print("yes min", min(yes_prices))
    print("no min", min(no_prices))
    print("sum", min(yes_prices)+min(no_prices))

asyncio.run(test_asks())
