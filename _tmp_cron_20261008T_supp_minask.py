import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            t = yp + np_
            if t <= 1.005:
                rows.append((t, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"min-ask scan over {len(markets)} markets; near-misses(<=1.005) using MIN asks: {len(rows)}")
    for t, q, yp, np_, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    # overall floor
    async def floor(): pass
    alls = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            alls.append(min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks))
    if alls:
        print(f"global min-ask floor: {min(alls):.4f} across {len(alls)} priced markets")

asyncio.run(supp())
