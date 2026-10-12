import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor_scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        # True best ask = min over ladder (CLOB /book returns asks DESC-sorted)
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        ysz = max((float(a['size']) for a in yb.asks if abs(float(a['price'])-yp) < 1e-9), default=0.0)
        nsz = max((float(a['size']) for a in nb.asks if abs(float(a['price'])-np_) < 1e-9), default=0.0)
        rows.append((yp + np_, m.question[:70], yp, np_, ysz, nsz, m.liquidity))
    rows.sort()
    return elapsed, priced, len(markets), rows

elapsed, priced, total_markets, rows = asyncio.run(floor_scan())

brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"floor_scan: {total_markets} markets, {priced} with two-sided asks, {elapsed:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
for t, q, yp, np_, ysz, nsz, liq in brackets:
    print(f"  {t:.4f} | Yes@{yp:.3f}({ysz:.0f}) No@{np_:.3f}({nsz:.0f}) | liq={liq} | {q}")
print(f"Near-misses (1.000 <= sum <= 1.005): {len(near)}")
for t, q, yp, np_, ysz, nsz, liq in near[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f}({ysz:.0f}) No@{np_:.3f}({nsz:.0f}) | liq={liq} | {q}")
print("Top-12 lowest best-ask totals (all priced markets):")
for t, q, yp, np_, ysz, nsz, liq in rows[:12]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
