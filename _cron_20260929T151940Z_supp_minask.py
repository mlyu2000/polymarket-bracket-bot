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

    brackets = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.0:
            brackets.append((total, yp, np, m.question[:60], m.liquidity))
        elif total <= 1.005:
            near.append((total, yp, np, m.question[:60], m.liquidity))
    brackets.sort()
    near.sort()
    return len(markets), scan_time, brackets, near

n, t, brackets, near = asyncio.run(scan())
print(f"[min-ask check] {n} markets in {t:.1f}s")
print(f"TRUE BRACKETS (min asks sum<1): {len(brackets)}")
for total, yp, np, q, liq in brackets[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"TRUE NEAR-MISSES (<=1.005): {len(near)}")
for total, yp, np, q, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if near:
    print(f"Best sum observed: {near[0][0]:.4f}")
