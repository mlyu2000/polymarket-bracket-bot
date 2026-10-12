import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    print(f"Fetched {len(markets)}")
    for m in markets[:5]:
        yes_id, no_id = m.clob_token_ids
        yb = await api.fetch_order_book(yes_id)
        nb = await api.fetch_order_book(no_id)
        if yb and nb and yb.asks and nb.asks:
            y_price = min(float(a['price']) for a in yb.asks)
            n_price = min(float(a['price']) for a in nb.asks)
            print(m.question[:60], y_price, n_price, y_price+n_price, m.liquidity)
asyncio.run(t())
