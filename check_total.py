import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check_total():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count=0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes, no = books[0]
        if not yes or not no or not yes.asks or not no.asks:
            continue
        yprice = min(float(a['price']) for a in yes.asks)
        nprice = min(float(a['price']) for a in no.asks)
        total = yprice + nprice
        if total < 1.0:
            print("FOUND", total, m.question[:80])
            count+=1
    print("total found", count)

asyncio.run(check_total())
