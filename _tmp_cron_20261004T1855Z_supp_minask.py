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

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        sums.append((yp + np, m.question[:55], yp, np, m.liquidity))

    sums.sort()
    print(f"min-ask scan: {len(markets)} markets, {len(sums)} with both books, {scan_time:.1f}s")
    print("--- true floor (best 8 by min-ask sum) ---")
    for s, q, yp, np, liq in sums[:8]:
        print(f"  {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    below = [x for x in sums if x[0] < 1.0]
    le1005 = [x for x in sums if x[0] <= 1.005]
    print(f"sums <1.00: {len(below)} | sums <=1.005: {len(le1005)}")
    for s, q, yp, np, liq in below:
        print(f"  RAW-BRACKET {s:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
