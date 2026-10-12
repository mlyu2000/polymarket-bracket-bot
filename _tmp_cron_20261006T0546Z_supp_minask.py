import asyncio, logging, time, json
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
    elapsed = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        priced += 1
        rows.append((total, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    return {'elapsed': elapsed, 'priced': priced, 'rows': rows}

res = asyncio.run(scan())
print(f"min-ask floor scan: {res['priced']} priced markets in {res['elapsed']:.1f}s")
brackets = [r for r in res['rows'] if r[0] < 1.0]
print(f"TRUE BRACKETS (sum<1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("Top-8 lowest sums (min-ask):")
for total, q, yp, np, liq in res['rows'][:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
near = [r for r in res['rows'] if 1.0 <= r[0] <= 1.005]
print(f"Near-misses (1.00-1.005): {len(near)}")
