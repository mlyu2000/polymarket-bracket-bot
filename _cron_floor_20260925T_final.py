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

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np, m.question[:50], yp, np, m.liquidity))
    sums.sort()
    return sums, scan_time, len(markets)

sums, t, n = asyncio.run(scan())
print(f"min-ask scan: {n} markets in {t:.1f}s; priced={len(sums)}")
brackets = [s for s in sums if s[0] < 1.0]
near = [s for s in sums if 1.0 <= s[0] <= 1.005]
print(f"true BRACKETS (best asks, sum<1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"true near-misses (<=1.005): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if sums:
    print(f"floor: {sums[0][0]:.3f} | {sums[0][1]}")
