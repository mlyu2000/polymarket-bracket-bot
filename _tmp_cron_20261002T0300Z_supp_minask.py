import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if total < 1.0:
            brackets.append((total, m.question[:60], ya, na, m.liquidity))
        if total <= 1.005:
            rows.append((total, m.question[:50], ya, na, m.liquidity))
    rows.sort()
    brackets.sort()
    return len(markets), dt, rows, brackets

n, dt, rows, brackets = asyncio.run(scan())
print(f"Supplemental BEST-ASK scan (min asks): {n} markets in {dt:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
for total, q, ya, na, liq in brackets[:10]:
    print(f"  *** {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
print(f"NEAR-MISSES (best-ask sum <= 1.005): {len(rows)}")
for total, q, ya, na, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
