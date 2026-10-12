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

    # Best-ask (min) based totals — asks are DESC-sorted, asks[0] is worst ask
    totals = []
    priced = 0
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        totals.append((total, m.question[:60], ya, na, m.liquidity))
        if total < 1.0:
            brackets.append((total, m.question[:70], ya, na, m.liquidity))

    totals.sort()
    brackets.sort()
    print(f"scan {len(markets)} markets priced={priced} in {scan_time:.1f}s")
    print(f"TRUE BRACKETS (best-ask sum<1.00): {len(brackets)}")
    for total, q, ya, na, liq in brackets[:10]:
        print(f"  sum={total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("lowest 8 best-ask sums:")
    for total, q, ya, na, liq in totals[:8]:
        print(f"  sum={total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
