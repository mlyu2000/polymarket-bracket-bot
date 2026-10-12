import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    return rows, priced, len(markets), time.time() - t0

rows, priced, total, dt = asyncio.run(scan())
print(f"markets={total} priced={priced} time={dt:.1f}s")
print(f"FLOOR (true best-ask): {rows[0][0]:.3f}" if rows else "no priced markets")
for r in rows[:10]:
    print(f"  {r[0]:.3f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
print(f"BRACKETS sum<1.00: {sum(1 for r in rows if r[0] < 1.00)}")
print(f"sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
