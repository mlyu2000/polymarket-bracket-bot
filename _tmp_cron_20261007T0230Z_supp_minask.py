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

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        ya = [float(a['price']) for a in yes_book.asks]
        na = [float(a['price']) for a in no_book.asks]
        yes_best, no_best = min(ya), min(na)
        total = yes_best + no_best
        rows.append((total, m.question[:55], yes_best, no_best, m.liquidity))

    rows.sort()
    return {'markets': len(markets), 'priced': priced, 'rows': rows, 't': scan_time}

r = asyncio.run(scan())
print(f"Supp best-ask scan: {r['markets']} markets ({r['priced']} priced) in {r['t']:.1f}s")
brackets = [x for x in r['rows'] if x[0] < 1.0]
print(f"Best-ask brackets (min-ask sum < 1.00): {len(brackets)}")
for total, q, yp, np, liq in brackets[:10]:
    print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print("Lowest 8 best-ask sums:")
for total, q, yp, np, liq in r['rows'][:8]:
    print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
