import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        rows.append((total, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return len(markets), rows, brackets

n, rows, brackets = asyncio.run(scan())
print(f"Markets scanned: {n}, priced: {len(rows)}")
print(f"BEST-ASK BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for t, q, yp, np_, liq in sorted(brackets):
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("TRUE FLOOR (best-ask sums, 5 lowest):")
for t, q, yp, np_, liq in rows[:5]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
