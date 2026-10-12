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
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np <= 0 or yp >= 1.0 or np >= 1.0:
            continue
        priced += 1
        rows.append((yp + np, m.question[:50], yp, np, m.liquidity))

    rows.sort()
    print(f"Supp (min-ask): {len(markets)} markets in {scan_time:.1f}s | {priced} priced pairs")
    strict = [r for r in rows if r[0] < 1.0]
    print(f"TRUE brackets (sum<1.00): {len(strict)}")
    for total, q, yp, np, liq in strict:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"Near-misses 1.000-1.005 (min-ask): {len(nm)}")
    for total, q, yp, np, liq in nm[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("Floor (10 lowest sums):")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
