import asyncio, logging, time
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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # best ask = min price (asks are DESC-sorted in CLOB payload)
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
priced = len(rows)
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"priced books: {priced}")
print(f"true brackets (best-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"near-misses (1.00..1.005): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if rows:
    print(f"lowest sums overall: " + ", ".join(f"{r[0]:.4f}" for r in rows[:8]))
