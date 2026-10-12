import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0
    results = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            results.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    results.sort()
    return results, len(markets), scan_time

results, n, st = asyncio.run(scan())
print(f"supp-scan: {n} markets in {st:.1f}s (best-ask/min based)")
brackets = [r for r in results if r[0] < 1.0]
near = [r for r in results if 1.0 <= r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"near-misses (1.00-1.005): {len(near)}")
for total, q, yp, np, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("floor (min sum):", f"{results[0][0]:.4f}", results[0][1][:50] if results else "")
