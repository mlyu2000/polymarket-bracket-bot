import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity, m.volume))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"Markets with two-sided asks: {priced}")
if rows:
    print(f"True floor (best-ask sum): {rows[0][0]:.4f} | {rows[0][1]}")
brk = [r for r in rows if r[0] < 1.0]
print(f"Best-ask brackets (sum<1.000): {len(brk)}")
for s, q, ya, na, liq, vol in brk[:10]:
    print(f"  sum={s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} vol={vol} | {q}")
nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"Near-miss 1.000-1.005: {len(nm)}")
for s, q, ya, na, liq, vol in nm[:10]:
    print(f"  sum={s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} vol={vol} | {q}")
print("Top-10 lowest sums overall:")
for s, q, ya, na, liq, vol in rows[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
