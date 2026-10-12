import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supplement():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    print(f"priced markets: {priced}")
    print("true floor / best 8 (min-ask sums):")
    for t, q, yp, np, liq in rows[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (min-ask sum <= 1.005): {len(nm)}")
    for t, q, yp, np, liq in nm:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    br = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (min-ask sum < 1.0): {len(br)}")
    return rows

asyncio.run(supplement())
