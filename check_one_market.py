import asyncio
from config import Config
from polymarket_api import PolymarketAPI

Config.SCAN_SORT_BY = 'liquidity'
Config.MAX_MARKETS_PER_SCAN = 50
Config.MIN_LIQUIDITY_USDC = 100

async def find_one():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets")
    m = markets[0]
    print(f"Market: {m.question[:80]} liquidity {m.liquidity}")
    books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
    yb, nb = books[0]
    print('yes book ok', yb is not None)
    print('no book ok', nb is not None)
    if yb:
        prices = [float(a['price']) for a in yb.asks[:5]]
        print('yes prices', prices)
    if nb:
        prices = [float(a['price']) for a in nb.asks[:5]]
        print('no prices', prices)

asyncio.run(find_one())
