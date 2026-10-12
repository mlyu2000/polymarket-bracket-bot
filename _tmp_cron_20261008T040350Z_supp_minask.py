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

    def best_ask(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)

    rows = []
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya = best_ask(yes_book)
        na = best_ask(no_book)
        if ya is None or na is None:
            continue
        total = ya + na
        if total < 1.0:
            brackets += 1
        rows.append((total, m.question[:50], ya, na, m.liquidity))

    rows.sort()
    priced = len(rows)
    print(f"[min-ask supp] {priced} priced markets of {len(markets)} in {scan_time:.1f}s; true brackets (min-ask sum<1.0): {brackets}")
    print(f"[min-ask supp] best 10 sums:")
    for total, q, ya, na, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
