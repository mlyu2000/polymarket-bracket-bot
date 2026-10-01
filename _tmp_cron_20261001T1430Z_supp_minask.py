"""Supplement: near-misses on BEST asks (min). CLOB /book returns asks
DESC-sorted, so asks[0] in the verbatim block is the WORST ask (~0.999) and
under-reports. detector.py correctly uses min(); this mirrors it for the
near-miss band and reports the true floor."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        if m.liquidity <= 0:
            continue
        ya = min(yb.asks, key=lambda a: float(a['price']))
        na = min(nb.asks, key=lambda a: float(a['price']))
        yp = float(ya['price']); np_ = float(na['price'])
        if yp >= 1.0 or np_ >= 1.0 or yp <= 0 or np_ <= 0:
            continue
        total = yp + np_
        rows.append((total, m.question[:55], yp, np_, m.liquidity,
                     int(float(ya['size'])), int(float(na['size']))))
    rows.sort()
    print(f"supp: {len(rows)} priced markets in {dt:.1f}s (best-ask totals)")
    if rows:
        print(f"true floor: {rows[0][0]:.4f}")
    else:
        print("no rows")
    brackets = [r for r in rows if r[0] < 1.0]
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"sum<1.00 best-ask (true brackets): {len(brackets)}")
    for r in brackets[:10]:
        print(f"  RED {r[0]:.4f} | Yes@{r[2]:.3f}(sz{r[5]}) No@{r[3]:.3f}(sz{r[6]}) | liq={r[4]} | {r[1]}")
    print(f"near-misses (1.000-1.005 best-ask): {len(near)}")
    for r in near[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f}(sz{r[5]}) No@{r[3]:.3f}(sz{r[6]}) | liq={r[4]} | {r[1]}")

asyncio.run(supp())
