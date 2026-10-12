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

    brackets = []      # min-ask sum < 1.00
    near_misses = []   # 1.00 <= min-ask sum <= 1.005
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        total = yes_best + no_best
        rec = (total, m.question[:50], yes_best, no_best, m.liquidity)
        if total < 1.00:
            opp = detector.detect(m, yes_book, no_book)
            brackets.append((rec, opp))
        elif total <= 1.005:
            near_misses.append(rec)

    brackets.sort(key=lambda x: x[0][0])
    near_misses.sort()
    print(f"min-ask scan: {priced}/{len(markets)} markets priced in {scan_time:.1f}s")
    print(f"TRUE BRACKETS (min-ask sum<1.00): {len(brackets)}")
    for (total, q, yp, np, liq), opp in brackets:
        det = "DETECTED" if opp else f"no-det (buffers/edge<{Config.MIN_PROFIT_MARGIN})"
        print(f"  sum={total:.4f} Yes@{yp:.3f} No@{np:.3f} liq={liq} | {det} | {q}")
    print(f"NEAR-MISSES (1.00<=sum<=1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  sum={total:.4f} Yes@{yp:.3f} No@{np:.3f} liq={liq} | {q}")
    allrecs = [b[0] for b in brackets] + near_misses
    if allrecs:
        print(f"FLOOR: min sum = {min(r[0] for r in allrecs):.4f}")

asyncio.run(scan())
