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

    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    return {'markets': len(markets), 'priced': priced, 'near': near, 't': scan_time}

r = asyncio.run(scan())
print(f"min-ask scan: {r['markets']} markets ({r['priced']} priced) in {r['t']:.1f}s")
print(f"true near-misses (min-ask sum <= 1.005): {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if r['near']:
    print(f"FLOOR: {r['near'][0][0]:.4f}")
