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
    scan_time = time.time() - t0

    near = []
    best = None
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        if best is None or total < best[0]:
            best = (total, m.question[:50], yp, np, m.liquidity)
        if total <= 1.005:
            near.append((total, m.question[:50], yp, np, m.liquidity))
    near.sort()
    return len(markets), priced, near, best, scan_time

markets, priced, near, best, st = asyncio.run(scan())
print(f"markets={markets} priced={priced} scan={st:.1f}s")
print(f"BEST (lowest sum, best-asks): {best[0]:.4f} | Yes@{best[2]:.3f} No@{best[3]:.3f} | liq={best[4]} | {best[1]}")
print(f"NEAR-MISS <=1.005 (best-asks): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
