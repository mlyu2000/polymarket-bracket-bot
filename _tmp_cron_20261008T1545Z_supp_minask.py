import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        rows.append((total, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    print(f"SUPP min-ask scan: {len(markets)} markets ({priced} with two-sided asks) in {elapsed:.1f}s")
    print("FLOOR (best 8 min-ask sums):")
    for total, q, yp, np_, liq in rows[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    band = [r for r in rows if r[0] <= 1.005]
    print(f"MIN-ASK BRACKETS (<1.00): {len(brackets)}")
    for total, q, yp, np_, liq in brackets:
        print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"BAND <=1.005 count: {len(band)}")
    nxt = [r for r in rows if r[0] > 1.005][:5]
    print("NEXT-OUT (just above band):")
    for total, q, yp, np_, liq in nxt:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(supp())
