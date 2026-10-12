import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        if yes_book and yes_book.asks:
            prices = [float(a['price']) for a in yes_book.asks[:5]]
            print(m.question[:60], prices)
            break

asyncio.run(test())
