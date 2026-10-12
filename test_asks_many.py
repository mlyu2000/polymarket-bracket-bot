import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for i,m in enumerate(markets[:10]):
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        if yes_book and yes_book.asks:
            prices = [float(a['price']) for a in yes_book.asks[:5]]
            print(i, m.question[:40], prices)
        await asyncio.sleep(0.1)

asyncio.run(test())
