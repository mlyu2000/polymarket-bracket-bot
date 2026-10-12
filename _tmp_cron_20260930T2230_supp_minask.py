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

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # /book asks are DESC-sorted; best ask = min
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return rows, len(markets), scan_time

rows, n, t = asyncio.run(scan())
print(f"SUPP best-ask totals: {n} markets in {t:.1f}s")
print(f"count with sum<=1.00: {sum(1 for r in rows if r[0] <= 1.0 + 1e-9)}")
print(f"count with sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005 + 1e-9)}")
print("top 8 lowest sums:")
for s, q, ya, na, liq in rows[:8]:
    print(f"  {s:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
