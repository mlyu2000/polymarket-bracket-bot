"""Min-ask supplement: same scan, but near-misses computed with best (lowest)
ask via min(), matching detector.py logic. The provided cron script uses
asks[0] which is the WORST ask (asks are DESC-sorted) -> always ~0.999."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps, near_misses = [], []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))
    near_misses.sort()
    return len(markets), priced, opps, near_misses, scan_time

markets, priced, opps, near_misses, scan_time = asyncio.run(scan())
print(f"[min-ask] {priced}/{markets} markets priced in {scan_time:.1f}s")
print(f"[min-ask] BRACKETS: {len(opps)}")
for o in opps:
    print(f"  {o.total_cost:.4f} | Yes@{o.yes_price:.3f} No@{o.no_price:.3f} | {o.question[:60]}")
print(f"[min-ask] Near-misses (<=1.005): {len(near_misses)}")
for total, q, yp, np_, liq in near_misses[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
if near_misses:
    print(f"[min-ask] floor: {near_misses[0][0]:.4f}")
