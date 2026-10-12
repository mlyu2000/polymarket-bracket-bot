"""Supplement: best-ask (min) based floor check.
Known issue: CLOB /book asks are DESC-sorted, so asks[0] in the verbatim
near-miss block is the WORST ask (~0.999) and always yields 0 near-misses.
This recomputes near-misses using the true best (min) ask, same as detector.py.
"""
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
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        tot = yp + np
        priced += 1
        rows.append((tot, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    return priced, rows

priced, rows = asyncio.run(scan())
print(f"Markets with priced books: {priced}")
near = [r for r in rows if r[0] <= 1.005]
under1 = [r for r in rows if r[0] < 1.0]
print(f"True best-ask sum < 1.00: {len(under1)}")
for tot, q, yp, np, liq in under1:
    print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"True best-ask near-misses (<=1.005): {len(near)}")
for tot, q, yp, np, liq in near[:10]:
    print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if rows:
    print(f"Floor (lowest sum): {rows[0][0]:.4f} | {rows[0][1]}")
