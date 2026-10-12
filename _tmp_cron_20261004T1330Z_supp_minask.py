import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
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
            brackets.append((total, yp, np_, m.question[:60], m.liquidity))
        elif total <= 1.005:
            rows.append((total, yp, np_, m.question[:50], m.liquidity))
    rows.sort()
    brackets.sort()
    return markets, brackets, rows

markets, brackets, rows = asyncio.run(scan())
print(f"MIN-ASK FLOOR CHECK: {len(markets)} markets")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for total, yp, np_, q, liq in brackets[:10]:
    print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Near-misses (min-ask, 1.000 < sum <= 1.005): {len(rows)}")
for total, yp, np_, q, liq in rows[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if rows:
    print(f"BEST FLOOR: {min([r[0] for r in rows] + [b[0] for b in brackets]):.4f}")
