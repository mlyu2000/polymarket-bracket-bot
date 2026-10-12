import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan_best():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    brackets = []
    near = []
    priced = 0
    best_floor = 10.0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total < best_floor:
            best_floor = total
        if total < 1.00:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))
    brackets.sort()
    near.sort()
    return len(markets), priced, brackets, near, dt, best_floor

n, priced, brackets, near, dt, best_floor = asyncio.run(scan_best())
print(f"=== SUPPLEMENT (best asks = min over ladder) ===")
print(f"Scanned {n} markets ({priced} with two-sided asks) in {dt:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np_, liq in brackets[:10]:
    print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"TRUE NEAR-MISSES (1.00 <= sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  🟡 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Lowest floor among priced markets: {best_floor:.4f}")
