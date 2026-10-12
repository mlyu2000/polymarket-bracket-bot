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
    dt = time.time() - t0

    priced = []      # markets with both books having asks
    best_totals = [] # (min_sum, q, yes_min, no_min, liq)
    bracket_min = [] # min-sum based < 1.00
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        priced.append(m)
        best_totals.append((total, m.question[:55], yes_min, no_min, m.liquidity))
        if total < 1.00:
            bracket_min.append((total, m.question[:55], yes_min, no_min, m.liquidity))
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print(f"DETECTOR HIT: {opp.total_cost:.4f} edge={opp.net_edge:.4f} | {m.question[:60]}")

    best_totals.sort()
    bracket_min.sort()
    print(f"markets={len(markets)} priced={len(priced)} scan_time={dt:.1f}s")
    print(f"MIN-ASK BRACKETS (best-ask sum < 1.00): {len(bracket_min)}")
    for t, q, yp, np_, liq in bracket_min[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("TOP-12 BEST MIN-ASK TOTALS:")
    for t, q, yp, np_, liq in best_totals[:12]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
