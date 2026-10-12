"""Supplement: same scan, but near-misses computed from BEST asks (min),
not asks[0] (CLOB returns asks DESC-sorted; asks[0] is worst ~0.999)."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            rows.append((total, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"Markets with both books priced: {priced}")
if rows:
    print(f"Floor (best sum overall): {rows[0][0]:.3f} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | {rows[0][1]}")
else:
    print("no priced markets")
print("Near-misses (best-ask sum <= 1.005):", sum(1 for r in rows if r[0] <= 1.005))
for total, q, yp, np_, liq in rows[:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
