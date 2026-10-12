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
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        yp = float(yes_ask['price']); np_ = float(no_ask['price'])
        total = yp + np_
        priced += 1
        rows.append((total, m.question[:50], yp, np_, m.liquidity))

    rows.sort()
    print(f"Best-ask (min) totals: {priced}/{len(markets)} priced markets in {scan_time:.1f}s")
    if rows:
        print(f"FLOOR: {rows[0][0]:.4f} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]} | {rows[0][1]}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"best-ask sum<1.00: {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("Top-10 closest (best-ask):")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
