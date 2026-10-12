"""Supplemental: near-misses computed with BEST ask (min price), not asks[0].
CLOB /book returns asks DESC-sorted, so asks[0] is the worst (~0.999) level.
Corrects the verbatim cron near-miss block using the same min() logic as detector.py."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    near = []
    floors = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            npr = min(float(a['price']) for a in nb.asks)
            total = yp + npr
            floors.append(total)
            if total <= 1.005:
                near.append((total, m.question[:50], yp, npr, m.liquidity))
    near.sort()
    floors.sort()
    print(f"supp scan {len(markets)} markets in {dt:.1f}s; priced={len(floors)}")
    if floors:
        print(f"true floor (min sum across priced markets): {floors[0]:.4f}")
    print(f"sums<=1.005 (best-ask): {len(near)}")
    for total, q, yp, npr, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")

asyncio.run(scan())
