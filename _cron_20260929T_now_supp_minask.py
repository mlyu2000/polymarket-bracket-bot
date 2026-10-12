# Supplemental: near-misses measured with BEST (min) asks, same as detector.py uses.
# The verbatim cron script's near-miss block uses asks[0], which on Polymarket CLOB
# books is the WORST ask (asks are DESC-sorted), so it always reports ~0 near-misses.
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
    priced = 0
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60], m.liquidity))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            floors.append(total)
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    opps.sort()
    near_misses.sort()
    print(f"[min-ask] markets={len(markets)} priced={priced} scan_time={scan_time:.1f}s")
    print(f"[min-ask] true floor (min sum) = {min(floors):.4f}" if floors else "[min-ask] no floors")
    print(f"[min-ask] BRACKETS via detector: {len(opps)}")
    for s, e, sh, q, liq in opps[:10]:
        print(f"  sum={s:.4f} edge={e:.4f} shares={sh} liq={liq} | {q}")
    print(f"[min-ask] Near-misses (sum<=1.005): {len(near_misses)}")
    for total, q, yp, np_, liq in near_misses[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
