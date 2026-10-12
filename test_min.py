import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    print("Fetched", len(markets))
    for m in markets[:3]:
        print(m.question[:80], m.liquidity)
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes, no = books[0]
        if yes and yes.asks:
            print(" yes best ask:", min(float(a['price']) for a in yes.asks))
        if no and no.asks:
            print(" no best ask:", min(float(a['price']) for a in no.asks))

asyncio.run(test())
