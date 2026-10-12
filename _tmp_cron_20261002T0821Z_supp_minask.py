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

    # Use BEST ask = min() (asks are DESC-sorted in CLOB /book response)
    totals = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.00:
            brackets.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            totals.append((total, m.question[:60], yp, np, m.liquidity))
    totals.sort()
    brackets.sort()
    print(f"supp-scan: {len(markets)} markets in {scan_time:.1f}s (best-ask basis)")
    print(f"best-ask BRACKETS (<1.00): {len(brackets)}")
    for t, q, yp, np, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"best-ask near-misses (1.000..1.005): {len(totals)}")
    for t, q, yp, np, liq in totals[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    # report floor across all priced markets
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        floors.append(yp + np)
    if floors:
        floors.sort()
        print(f"floor across {len(floors)} priced markets: min={floors[0]:.4f} p10={floors[len(floors)//10]:.4f} median={floors[len(floors)//2]:.4f}")

asyncio.run(scan())
