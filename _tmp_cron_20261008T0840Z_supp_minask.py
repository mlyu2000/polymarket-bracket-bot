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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            total = ya + na
            rows.append((total, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"MIN-ASK totals (best 10 of {len(rows)} priced markets):")
for total, q, ya, na, liq in rows[:10]:
    flag = "BRACKET" if total < 1.0 else ("near" if total <= 1.005 else "")
    print(f"  {total:.4f} {flag} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"true_min_brackets(sum<1.000)={len(brackets)} true_min_near(<=1.005)={len(near)}")
