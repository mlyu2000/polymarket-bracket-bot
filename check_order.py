import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print(m.question[:80])
    books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
    yes, no = books[0]
    print("yes asks first 10:", yes.asks[:10])
    print("no asks first 10:", no.asks[:10])

asyncio.run(check())
