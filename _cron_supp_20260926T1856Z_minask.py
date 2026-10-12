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
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return priced, dt, rows

priced, dt, rows = asyncio.run(scan())
print(f"Supplement (best-ask=min): {priced} priced markets in {dt:.1f}s")
print(f"Sum<1.000: {sum(1 for r in rows if r[0] < 1.0)}")
print(f"Sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
print(f"Sum<=1.010: {sum(1 for r in rows if r[0] <= 1.010)}")
print("Top 8 lowest sums (best-ask):")
for total, q, yp, np, liq in rows[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
