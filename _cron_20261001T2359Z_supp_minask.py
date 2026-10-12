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
    el = time.time() - t0
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            priced += 1
            if total <= 1.005:
                rows.append((total, m.question[:50], yp, np, m.liquidity))
    rows.sort()
    return len(markets), priced, rows, el

n, priced, rows, el = asyncio.run(scan())
print(f"⏱ best-ask (min) recomputation: {n} markets, {priced} with priced books in {el:.1f}s")
print(f"🔴 True brackets (min-ask sum < 1.00): {sum(1 for r in rows if r[0] < 1.0)}")
print(f"📊 Near-misses (best-ask sum <= 1.005): {len(rows)}")
for total, q, yp, np, liq in rows[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
