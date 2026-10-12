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

    best = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            best.append((total, m.question[:50], yp, np, m.liquidity))
    best.sort()
    brackets.sort()
    return len(markets), dt, best, brackets

n, dt, best, brackets = asyncio.run(scan())
print(f"⏱ best-ask rescan: {n} markets in {dt:.1f}s")
print(f"✅ REAL BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets:
    print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"📊 NEAR-MISSES (best-ask sum ≤1.005): {len(best)}")
for total, q, yp, np, liq in best[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
