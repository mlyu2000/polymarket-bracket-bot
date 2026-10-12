# Supplementary: near-misses using BEST ask (min price), matching detector.py logic.
# The verbatim script's asks[0] is the WORST ask (CLOB returns asks DESC-sorted),
# so its near-miss list is unreliable. This scan recomputes near-misses correctly.
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

    opps = []
    near_misses = []
    brackets_any = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total < 1.0:
                brackets_any.append((total, m.question[:60], yp, np, m.liquidity))
            elif total <= 1.005:
                near_misses.append((total, m.question[:60], yp, np, m.liquidity))

    brackets_any.sort()
    near_misses.sort()
    print(f"SUPP best-ask scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"true sum<1.00 markets: {len(brackets_any)}")
    for t, q, yp, np, liq in brackets_any[:10]:
        print(f"  [TRUE-BRACKET] {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"best-ask near-misses (1.00<sum<=1.005): {len(near_misses)}")
    for t, q, yp, np, liq in near_misses[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    # distribution of all sums for context
    sums = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            sums.append(min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks))
    if sums:
        sums.sort()
        print(f"priced books: {len(sums)} | min sum {sums[0]:.4f} | median {sums[len(sums)//2]:.4f} | p90 {sums[int(len(sums)*0.9)]:.4f}")

asyncio.run(scan())
