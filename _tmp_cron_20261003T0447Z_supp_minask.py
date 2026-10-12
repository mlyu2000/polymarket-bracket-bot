"""Supplementary: near-miss floor using BEST asks (min price).
CLOB /book asks are DESC-sorted so asks[0] is the worst ask; detector.py
correctly uses min(). This mirrors the detector's pricing for the near band."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    sums = []
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        if m.liquidity <= 0:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        s = ya + na
        priced += 1
        sums.append(s)
        if s < 1.0:
            brackets.append((s, m.question[:60], ya, na, m.liquidity))
    sums.sort()
    brackets.sort()
    print(f"Markets: {len(markets)}, priced both-sides: {priced}")
    print(f"True brackets (best-ask sum<1.00): {len(brackets)}")
    for s, q, ya, na, liq in brackets[:10]:
        print(f"  sum={s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"Lowest 8 best-ask sums (floor):")
    for s in sums[:8]:
        print(f"  {s:.4f}")
    near = [x for x in sums if x <= 1.005]
    print(f"Near-misses (best-ask sum <=1.005): {len(near)}")

asyncio.run(scan())
