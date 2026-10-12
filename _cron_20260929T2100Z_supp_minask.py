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

    priced = 0
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        rows.append((total, m.question[:60], ya, na, m.liquidity))
        if total < 1.0:
            opp = detector.detect(m, yes_book, no_book)
            print(f"  SUB-1.00 DETECTOR: {m.question[:60]} -> {'FIRED' if opp else 'no (filters)'}")
    rows.sort()
    print(f"Supp best-ask scan: {priced}/{len(markets)} priced markets in {scan_time:.1f}s")
    print("True floor (min-ask sums), 10 lowest:")
    for total, q, ya, na, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    n_le_1005 = sum(1 for r in rows if r[0] <= 1.005)
    n_lt_1 = sum(1 for r in rows if r[0] < 1.0)
    print(f"Near-misses (best-ask sum <= 1.005): {n_le_1005} | sum < 1.00: {n_lt_1}")

asyncio.run(scan())
