import asyncio, logging
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
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        # asks are DESC-sorted: best ask = min
        yes_ask = min(float(a['price']) for a in yes_book.asks)
        no_ask = min(float(a['price']) for a in no_book.asks)
        rows.append((yes_ask + no_ask, m.question[:60], yes_ask, no_ask, m.liquidity))
    rows.sort()
    return len(markets), priced, rows

markets, priced, rows = asyncio.run(scan())
print(f"Markets fetched: {markets} | priced (both books have asks): {priced}")
if rows:
    print(f"TRUE floor (min-ask method): best sum = {rows[0][0]:.4f}")
print("Top 10 lowest sums (best-ask Yes + best-ask No):")
for total, q, yp, np_, liq in rows[:10]:
    flag = "<<< BRACKET <1.00" if total < 1.0 else ("near-miss <=1.005" if total <= 1.005 else "")
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q} {flag}")
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"SUMMARY: true brackets (<1.00): {len(brackets)} | near-misses (1.00-1.005): {len(near)}")
