"""Supplementary near-miss scan using BEST asks (min price).
Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst ask;
the verbatim cron near-miss block under-reports. detector.py itself uses min()
correctly, so the BRACKETS section of the verbatim run is accurate as-is.
Run twice for consistency (established cron practice)."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    all_totals = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            t = yp + np_
            all_totals.append((t, m.question[:50], yp, np_))
            if t <= 1.005:
                near.append((t, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    sums = sorted(x[0] for x in all_totals)
    le1010 = sum(1 for s in sums if s <= 1.010)
    print(f"Markets fetched: {len(markets)}; both-sides-priced: {len(sums)}")
    if sums:
        print(f"True floor (min sum of best asks): {sums[0]:.4f}")
        print(f"Count <=1.010: {le1010}")
        print(f"Bottom-10 sums: {[round(s,4) for s in sums[:10]]}")
    print(f"Near-misses (best-ask sum <= 1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
