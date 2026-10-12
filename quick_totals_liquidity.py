import asyncio
from config import Config
from polymarket_api import PolymarketAPI

Config.SCAN_SORT_BY = 'liquidity'
Config.MAX_MARKETS_PER_SCAN = 100
Config.MIN_LIQUIDITY_USDC = 0

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets")
    total = 0
    for m in markets[:20]:
        if m.liquidity < 100:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yb, nb = books[0]
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            s = yp + np
            total += 1
            print(f"{s:.3f} yes {yp:.3f} no {np:.3f} liq {m.liquidity:.0f} | {m.question[:60]}")
    print(f"Checked {total}")

asyncio.run(scan())
