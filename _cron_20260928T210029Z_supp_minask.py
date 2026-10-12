# Supplementary: near-misses computed from BEST asks (min of asks),
# since Polymarket /book returns asks DESC-sorted and asks[0] is the worst ask.
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if not opp and yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np, m.liquidity))

    near_misses.sort()
    return len(markets), priced, scan_time, near_misses

markets_n, priced, scan_time, near_misses = asyncio.run(scan())
print(f"[best-ask supplement] {markets_n} markets ({priced} priced non-bracket pairs) in {scan_time:.1f}s")
print(f"Near-misses best-ask (sum<=1.005): {len(near_misses)}")
for total, q, yp, np, liq in near_misses[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
