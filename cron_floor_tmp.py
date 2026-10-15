import asyncio, logging, time, json
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

    rows = []
    two_sided = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        # TRUE floor = min of ALL asks on each side (asks are DESC-sorted on CLOB)
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        min_yes = min(float(a['price']) for a in yes_book.asks)
        min_no = min(float(a['price']) for a in no_book.asks)
        total = min_yes + min_no
        two_sided += 1
        rows.append((total, m.question[:70], min_yes, min_no, m.liquidity))

        # cross-check with detector (mechanism-agnostic)
        if total < 1.00:
            opp = detector.detect(m, yes_book, no_book)
            if opp:
                print(f"BRACKET DETECTED: {m.question} sum={opp.total_cost}")

    rows.sort()
    yes_only = len(markets) - two_sided
    print(f"🔍 True-floor scan: {len(markets)} markets in {scan_time:.1f}s | two-sided={two_sided} yes-only={yes_only}")
    print("FLOOR (min both legs, all asks):")
    for total, q, yp, np, liq in rows[:12]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    # distribution buckets
    for thresh in (1.010, 1.020, 1.050):
        n = sum(1 for r in rows if r[0] <= thresh)
        print(f"le{thresh:.3f} n={n}")
    n_below = sum(1 for r in rows if r[0] < 1.000)
    print(f"lt1.000 n={n_below}")
    if rows:
        print(f"FLOOR_HISTORY_TAIL: {rows[0][0]:.3f}")

asyncio.run(scan())
