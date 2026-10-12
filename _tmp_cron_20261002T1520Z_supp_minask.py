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
    scan_time = time.time() - t0

    results = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.0:
            brackets.append((total, yp, np_, m.question[:60], m.liquidity))
        elif total <= 1.005:
            results.append((total, yp, np_, m.question[:50], m.liquidity))
    results.sort()
    return markets, scan_time, brackets, results

markets, scan_time, brackets, near = asyncio.run(scan())
print(f"MIN-ASK floor check: {len(markets)} markets in {scan_time:.1f}s")
print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
for total, yp, np_, q, liq in sorted(brackets):
    print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Near-misses (min-ask sum <=1.005): {len(near)}")
for total, yp, np_, q, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
