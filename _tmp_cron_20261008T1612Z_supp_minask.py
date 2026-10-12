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
    true_brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        sums.append((total, m.question[:55], yp, np, m.liquidity))
        if total < 1.0:
            true_brackets.append((total, m.question[:55], yp, np, m.liquidity))
    sums.sort()
    return markets, sums, true_brackets, scan_time

markets, sums, true_brackets, scan_time = asyncio.run(scan())
priced = len(sums)
print(f"Supp min-ask scan: {len(markets)} markets, {priced} priced, {scan_time:.1f}s")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(true_brackets)}")
for t, q, yp, np, liq in sorted(true_brackets):
    print(f"  B {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("FLOOR (5 lowest min-ask sums):")
for t, q, yp, np, liq in sums[:5]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
n_le_1005 = sum(1 for s in sums if s[0] <= 1.005)
n_le_101 = sum(1 for s in sums if s[0] <= 1.01)
print(f"count sum<=1.005: {n_le_1005} | sum<=1.01: {n_le_101}")
