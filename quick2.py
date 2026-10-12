import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
    yes, no = books[0]
    print("yes asks", len(yes.asks) if yes else 0)
    print("no asks", len(no.asks) if no else 0)
    if yes and yes.asks:
        print("yes best", min(float(a['price']) for a in yes.asks))
    if no and no.asks:
        print("no best", min(float(a['price']) for a in no.asks))

asyncio.run(f())
