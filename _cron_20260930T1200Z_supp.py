"""Supplement: near-misses using min-ask (corrected best-ask resolution)."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    near = []
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            floors.append(total)
            if total < 1.005 and m.liquidity > 0:
                near.append((total, m.question[:55], yp, np_, m.liquidity))
    near.sort()
    floors.sort()
    return markets, near, floors, scan_time

markets, near, floors, st = asyncio.run(scan())
print(f"min-ask scan: {len(markets)} markets in {st:.1f}s")
print(f"BRACKETS sum<1.000 (min-ask, liq>0): {sum(1 for t,_,_,_,_ in near if t < 1.0)}")
print(f"Near-misses <=1.005 (min-ask): {len(near)}")
for t, q, yp, np_, liq in near[:8]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if floors:
    print(f"floor sums (best 5 across all liq): {[f'{x:.3f}' for x in floors[:5]]}")
