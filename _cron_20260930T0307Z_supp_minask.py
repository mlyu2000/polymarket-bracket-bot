import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    brackets_min = []
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        s = ya + na
        rows.append((s, m.question[:50], ya, na, m.liquidity))
        if s < 1.0:
            brackets_min.append((s, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"min-ask floor: {rows[0][0]:.4f} ({rows[0][1]}) Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f}")
    print(f"markets priced: {len(rows)}")
    print(f"min-ask brackets (<1.00): {len(brackets_min)}")
    for s, q, ya, na, liq in sorted(brackets_min)[:10]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("closest 8 sums (min-ask):")
    for s, q, ya, na, liq in rows[:8]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses <=1.005 (min-ask): {len(nm)}")

asyncio.run(supp())
